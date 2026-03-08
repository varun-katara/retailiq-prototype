import pandas as pd
import numpy as np
from typing import Dict, List
from datetime import datetime, timedelta

class InventoryOptimizer:
    """Calculates reorder recommendations and stockout risk scores"""
    
    @staticmethod
    def calculate_stockout_risk(
        current_stock: int,
        forecast_demand: float,
        forecast_std: float,
        lead_time_days: int = 7
    ) -> float:
        """
        Calculates stockout risk score (0-100).
        
        Args:
            current_stock: Current inventory level
            forecast_demand: Predicted demand during lead time
            forecast_std: Standard deviation of forecast
            lead_time_days: Supplier lead time in days
            
        Returns:
            Risk score from 0 (no risk) to 100 (certain stockout)
        """
        # Calculate safety stock (95% service level)
        safety_stock = 1.65 * forecast_std
        
        # Calculate risk score
        required_stock = forecast_demand + safety_stock
        
        if required_stock <= 0:
            return 0.0
        
        risk_score = 100 * (1 - (current_stock / required_stock))
        
        # Bound between 0 and 100
        return max(0.0, min(100.0, risk_score))
    
    @staticmethod
    def calculate_reorder_point(
        avg_daily_demand: float,
        lead_time_days: int,
        forecast_std: float
    ) -> int:
        """
        Calculates reorder point.
        
        Args:
            avg_daily_demand: Average daily demand
            lead_time_days: Supplier lead time
            forecast_std: Standard deviation of forecast
            
        Returns:
            Reorder point (inventory level to trigger reorder)
        """
        safety_stock = 1.65 * forecast_std
        reorder_point = (avg_daily_demand * lead_time_days) + safety_stock
        return int(np.ceil(reorder_point))
    
    @staticmethod
    def calculate_reorder_quantity(
        avg_daily_demand: float,
        lead_time_days: int,
        review_period_days: int = 7
    ) -> int:
        """
        Calculates recommended reorder quantity.
        
        Args:
            avg_daily_demand: Average daily demand
            lead_time_days: Supplier lead time
            review_period_days: Inventory review period
            
        Returns:
            Recommended order quantity
        """
        # Simple approach: order enough for lead time + review period
        order_quantity = avg_daily_demand * (lead_time_days + review_period_days)
        return int(np.ceil(order_quantity))
    
    @staticmethod
    def estimate_stockout_date(
        current_stock: int,
        avg_daily_demand: float
    ) -> datetime:
        """
        Estimates when stockout will occur.
        
        Args:
            current_stock: Current inventory level
            avg_daily_demand: Average daily demand
            
        Returns:
            Estimated stockout date
        """
        if avg_daily_demand <= 0:
            return None
        
        days_until_stockout = current_stock / avg_daily_demand
        return datetime.now() + timedelta(days=int(days_until_stockout))
    
    @staticmethod
    def generate_recommendations(
        current_inventory: Dict[str, int],
        forecast_data: Dict[str, Dict],
        lead_time_days: int = 7
    ) -> List[Dict]:
        """
        Generates reorder recommendations for all products.
        
        Args:
            current_inventory: Dict mapping product_id to current stock level
            forecast_data: Dict mapping product_id to forecast results
            lead_time_days: Supplier lead time
            
        Returns:
            List of reorder recommendations sorted by risk score
        """
        recommendations = []
        
        for product_id, current_stock in current_inventory.items():
            if product_id not in forecast_data:
                continue
            
            forecast = forecast_data[product_id]
            
            if forecast.get('status') != 'success':
                continue
            
            predictions = forecast['predictions']
            
            # Calculate metrics from forecast
            predicted_quantities = [p['predicted_quantity'] for p in predictions[:lead_time_days]]
            forecast_demand = sum(predicted_quantities)
            avg_daily_demand = forecast_demand / lead_time_days
            
            # Calculate standard deviation from confidence intervals
            upper_bounds = [p['upper_bound'] for p in predictions[:lead_time_days]]
            lower_bounds = [p['lower_bound'] for p in predictions[:lead_time_days]]
            forecast_std = np.mean([(u - l) / 2 for u, l in zip(upper_bounds, lower_bounds)])
            
            # Calculate stockout risk
            risk_score = InventoryOptimizer.calculate_stockout_risk(
                current_stock, forecast_demand, forecast_std, lead_time_days
            )
            
            # Calculate reorder point
            reorder_point = InventoryOptimizer.calculate_reorder_point(
                avg_daily_demand, lead_time_days, forecast_std
            )
            
            # Only recommend if below reorder point
            if current_stock < reorder_point:
                # Calculate recommended quantity
                recommended_quantity = InventoryOptimizer.calculate_reorder_quantity(
                    avg_daily_demand, lead_time_days
                )
                
                # Estimate stockout date
                stockout_date = InventoryOptimizer.estimate_stockout_date(
                    current_stock, avg_daily_demand
                )
                
                # Determine priority
                if risk_score > 70:
                    priority = 'high'
                elif risk_score > 40:
                    priority = 'medium'
                else:
                    priority = 'low'
                
                # Generate reasoning
                reasoning = f"Current stock ({current_stock}) is below reorder point ({reorder_point}). "
                reasoning += f"Expected demand over next {lead_time_days} days: {int(forecast_demand)} units. "
                reasoning += f"Stockout risk: {risk_score:.1f}%."
                
                recommendations.append({
                    'product_id': product_id,
                    'product_name': forecast.get('product_name', product_id),
                    'current_stock': current_stock,
                    'reorder_point': reorder_point,
                    'recommended_quantity': recommended_quantity,
                    'stockout_risk_score': round(risk_score, 2),
                    'priority': priority,
                    'lead_time_days': lead_time_days,
                    'estimated_stockout_date': stockout_date.isoformat() if stockout_date else None,
                    'reasoning': reasoning
                })
        
        # Sort by risk score (highest first)
        recommendations.sort(key=lambda x: x['stockout_risk_score'], reverse=True)
        
        return recommendations
