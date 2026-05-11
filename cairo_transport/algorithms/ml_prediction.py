import pandas as pd
from sklearn.ensemble import RandomForestRegressor
from sklearn.model_selection import train_test_split
from sklearn.metrics import mean_squared_error, r2_score

from core.data import EXISTING_ROADS, TRAFFIC_FLOW

def prepare_data():
    records = []
    periods = {"morning": 0, "afternoon": 1, "evening": 2, "night": 3}
    
    for (u, v, dist, cap, cond) in EXISTING_ROADS:
        tf = TRAFFIC_FLOW.get((u, v)) or TRAFFIC_FLOW.get((v, u)) or {}
        
        for period, encoded_period in periods.items():
            flow = tf.get(period, cap * 0.5)
            ratio = min(flow / cap, 1.2) # Cap at 1.2 for realistic modeling
            
            records.append({
                "u": u, "v": v,
                "distance": dist,
                "capacity": cap,
                "condition": cond,
                "period": period,
                "period_encoded": encoded_period,
                "flow": flow,
                "congestion_ratio": ratio
            })
            
    df = pd.DataFrame(records)
    return df

def train_congestion_model():
    """
    Trains a Random Forest Regressor to predict congestion ratio.
    Returns the trained model and metrics.
    """
    df = prepare_data()
    
    features = ['distance', 'capacity', 'condition', 'period_encoded']
    X = df[features]
    y = df['congestion_ratio']
    
    X_train, X_test, y_train, y_test = train_test_split(X, y, test_size=0.2, random_state=42)
    
    model = RandomForestRegressor(n_estimators=100, random_state=42)
    model.fit(X_train, y_train)
    
    y_pred = model.predict(X_test)
    mse = mean_squared_error(y_test, y_pred)
    r2 = r2_score(y_test, y_pred)
    
    return model, df, mse, r2

def predict_congestion(model, distance, capacity, condition, period_name):
    """Predicts congestion ratio for a given hypothetical road segment."""
    periods = {"morning": 0, "afternoon": 1, "evening": 2, "night": 3}
    encoded = periods.get(period_name.lower(), 0)
    
    X_new = pd.DataFrame([{
        "distance": distance,
        "capacity": capacity,
        "condition": condition,
        "period_encoded": encoded
    }])
    
    return model.predict(X_new)[0]

if __name__ == "__main__":
    print("Training ML Congestion Predictor...")
    model, df, mse, r2 = train_congestion_model()
    print(f"Model trained successfully!")
    print(f"Dataset size: {len(df)} records")
    print(f"MSE: {mse:.4f}")
    print(f"R² Score: {r2:.4f}")
    
    # Test a prediction
    pred = predict_congestion(model, 10.0, 3000, 7, "morning")
    print(f"\nHypothetical 10km, 3000 cap, condition 7 road in the morning:")
    print(f"Predicted Congestion Ratio: {pred*100:.1f}%")
