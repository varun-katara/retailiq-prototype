import pandas as pd
import numpy as np
from datetime import datetime, timedelta
from typing import List, Dict, Tuple
from prophet import Prophet
from utils.regional_factors import RegionalFactors

class DemandForecaster:
    """Generates demand forecasts using Prophet or moving average fallback"""
    
    MIN_DATA_DAYS = 60
    
    @staticmethod
    def moving_average_forecast(df: pd.DataFrame, horizon: int, window: int = 7) -> pd.DataFrame:
        """
        Simple moving average forecast (fallback for insufficient data).
        
        Args:
            df: DataFrame with 'date' and 'quantity' columns
            horizon: Number of days to forecast
            window: Moving average window size
            
        Returns:
            DataFrame with forecast predictions
        """
        # Calculate moving average
        ma = df['quantity'].rolling(window=window, min_periods=1).mean().iloc[-1]
        
        # Generate future dates
        last_date = df['date'].max()
        future_dates = [last_date + timedelta(days=i+1) for i in range(horizon)]
        
        # Create forecast dataframe
        forecast_df = pd.DataFrame({
            'date': future_dates,
            'predicted_quantity': [ma] * horizon,
            'lower_bound': [ma * 0.8] * horizon,
            'upper_bound': [ma * 1.2] * horizon,
            'lower_bound_95': [ma * 0.7] * horizon,
            'upper_bound_95': [ma * 1.3] * horizon
        })
        
        return forecast_df
    
    @staticmethod
    def prophet_forecast(df: pd.DataFrame, horizon: int, region: str = None) -> pd.DataFrame:
        """
        Prophet-based forecast with regional factors.
        
        Args:
            df: DataFrame with 'date' and 'quantity' columns
            horizon: Number of days to forecast (7, 14, or 30)
            region: Region name for festival dates
            
        Returns:
            DataFrame with forecast predictions
        """
        # Prepare data for Prophet (requires 'ds' and 'y' columns)
        prophet_df = df[['date', 'quantity']].copy()
        prophet_df.columns = ['ds', 'y']
        prophet_df['ds'] = pd.to_datetime(prophet_df['ds'])
        
        # Initialize Prophet model
        model = Prophet(
            daily_seasonality=True,
            weekly_seasonality=True,
            yearly_seasonality=True,
            interval_width=0.8  # 80% confidence interval
        )
        
        # Add festival dates as holidays
        start_date = prophet_df['ds'].min()
        end_date = prophet_df['ds'].max() + timedelta(days=horizon)
        festivals = RegionalFactors.get_festival_dates(start_date, end_date)
        
        if not festivals.empty:
            model.add_country_holidays(country_name='IN')
        
        # Fit model
        model.fit(prophet_df)
        
        # Create future dataframe
        future = model.make_future_dataframe(periods=horizon)
        
        # Generate forecast
        forecast = model.predict(future)
        
        # Extract only future predictions
        forecast_future = forecast.tail(horizon).copy()
        
        # Format output
        result_df = pd.DataFrame({
            'date': forecast_future['ds'],
            'predicted_quantity': forecast_future['yhat'].clip(lower=0),  # No negative predictions
            'lower_bound': forecast_future['yhat_lower'].clip(lower=0),
            'upper_bound': forecast_future['yhat_upper'].clip(lower=0),
            'lower_bound_95': (forecast_future['yhat'] - 2 * (forecast_future['yhat_upper'] - forecast_future['yhat'])).clip(lower=0),
            'upper_bound_95': (forecast_future['yhat'] + 2 * (forecast_future['yhat_upper'] - forecast_future['yhat'])).clip(lower=0)
        })
        
        return result_df
    
    @staticmethod
    def generate_forecast(df: pd.DataFrame, product_id: str, horizon: int, region: str = None) -> Dict:
        """
        Main forecast generation function with automatic fallback.
        
        Args:
            df: Sales data DataFrame
            product_id: Product to forecast
            horizon: Forecast period (7, 14, or 30 days)
            region: Region name
            
        Returns:
            Dict with forecast results and metadata
        """
        # Filter data for specific product
        product_df = df[df['product_id'] == product_id].copy()
        
        if len(product_df) == 0:
            return {
                'error': f'No data found for product {product_id}',
                'status': 'error'
            }
        
        # Sort by date
        product_df = product_df.sort_values('date')
        
        # Check data sufficiency
        data_days = (product_df['date'].max() - product_df['date'].min()).days
        use_prophet = data_days >= DemandForecaster.MIN_DATA_DAYS
        
        # Generate forecast
        if use_prophet:
            try:
                forecast_df = DemandForecaster.prophet_forecast(product_df, horizon, region)
                method = 'prophet'
                warning = None
            except Exception as e:
                # Fallback to moving average if Prophet fails
                forecast_df = DemandForecaster.moving_average_forecast(product_df, horizon)
                method = 'moving_average'
                warning = f'Prophet failed ({str(e)}), using moving average fallback'
        else:
            forecast_df = DemandForecaster.moving_average_forecast(product_df, horizon)
            method = 'moving_average'
            warning = f'Insufficient data ({data_days} days < {DemandForecaster.MIN_DATA_DAYS} days required), using moving average fallback'
        
        # Calculate MAPE on historical data (simple accuracy metric)
        if len(product_df) > 7:
            recent_actual = product_df['quantity'].tail(7).values
            recent_predicted = [product_df['quantity'].tail(14).head(7).mean()] * 7
            mape = np.mean(np.abs((recent_actual - recent_predicted) / recent_actual)) * 100
        else:
            mape = None
        
        return {
            'status': 'success',
            'product_id': product_id,
            'horizon_days': horizon,
            'method': method,
            'warning': warning,
            'accuracy_mape': mape,
            'predictions': forecast_df.to_dict('records'),
            'generated_at': datetime.now().isoformat()
        }
