import xgboost as xgb
from sklearn.linear_model import LinearRegression

def train_evaluation_models(X_train, y_train):
    # Train Baseline
    lr_model = LinearRegression().fit(X_train, y_train)
    
    # Train AI Model (Stable, high-accuracy settings)
    ml_model = xgb.XGBRegressor(
        n_estimators=100, 
        learning_rate=0.05, 
        max_depth=3, 
        colsample_bytree=0.8,
        subsample=0.8,
        min_child_weight=2, 
        random_state=42
    )
    ml_model.fit(X_train, y_train)
    
    return lr_model, ml_model

def train_future_models(X, y):
    # Train Full Baseline
    lr_model_full = LinearRegression().fit(X, y)
    
    # Train Full AI Model (Stable, high-accuracy settings)
    ml_model_full = xgb.XGBRegressor(
        n_estimators=100, 
        learning_rate=0.05, 
        max_depth=3, 
        colsample_bytree=0.8,
        subsample=0.8,
        min_child_weight=2, 
        random_state=42
    )
    ml_model_full.fit(X, y)
    
    return lr_model_full, ml_model_full