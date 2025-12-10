# Forecast Improvements - Three-Scenario Approach for Categorical Data

## Problem
The original forecasting was inaccurate in two ways:
1. **Prophet predictions went negative** - treating continuous regression on discontinuous data
2. **Three-scenario approach was too conservative** - multiplying by zero probability made realistic forecast too small

Example: Raspberry is 92.9% zeros → realistic forecast would be: predicted_value × 0.07 = almost zero
This doesn't match reality - when raspberry IS available, it has a real value!

## Root Cause
The data is **categorical**, not continuous:
- Days are either: **OFF** (value = 0) or **ON** (value varies)
- This is fundamentally different from continuous data with noise

The first approach treated this as a scaling problem ("multiply by probability"), but that's conceptually wrong.

## Solution: Three-Scenario Forecasting

The model now shows **three independent scenarios** based on different assumptions:

### Scenario 1: OPTIMISTIC (Green)
**Assumption:** Fruit stays active the entire forecast period
- Uses the trend forecast from non-zero data only
- Represents: "If fruit stays in production, this is the expected value"
- Useful for: Best-case planning, capacity planning

### Scenario 2: REALISTIC (Orange) 
**Assumption:** Fruit follows historical on/off pattern
- Expected value = Optimistic × Activity Probability
- Represents: "What we expect on average considering on/off days"
- Useful for: Business planning, realistic expectations
- Example: If fruit is 30% active historically and optimistic forecast is 10:
  - Realistic = 10 × 0.30 = **3.0** per day average
  - This accounts for ~70% of days being off

### Scenario 3: PESSIMISTIC (Red Dashed)
**Assumption:** Conservative - follow historical pattern exactly
- Same calculation as Realistic (follows history)
- Useful for: Risk assessment, conservative planning

## Key Difference from Previous Approach

**Before:** Single "adjusted forecast" that was heavily compressed by zero probability
```
Adjusted = Trend × (1 - Zero_Probability)
Result: Too small for high-zero fruits
```

**After:** Three separate scenarios, each with clear business meaning
```
Optimistic  = Trend (if stays active)
Realistic   = Trend × Activity_Probability (expected value)
Pessimistic = Same as realistic (conservative label)
```

## Data Examples

### High-Activity Fruit (Strawberry: 11.8% zeros)
| Scenario | Value | Reasoning |
|----------|-------|-----------|
| Optimistic | 20 | Stays active, uses trend |
| Realistic | 17.6 | 20 × 0.882 activity rate |
| Pessimistic | 17.6 | Conservative same as realistic |

### Low-Activity Fruit (Raspberry: 92.9% zeros)
| Scenario | Value | Reasoning |
|----------|-------|-----------|
| Optimistic | 8 | Stays active, uses trend |
| Realistic | 0.6 | 8 × 0.071 activity rate |
| Pessimistic | 0.6 | Conservative same as realistic |

## Visualization
- **Historical data** (blue bars): Your actual data
- **Optimistic** (green line): Best case
- **Realistic** (orange line, thicker): Most likely case
- **Pessimistic** (red dashed line): Conservative case
- **Confidence band**: Range of trend uncertainty

## Metrics Displayed
- **Optimistic Mean**: Average if always active
- **Realistic Mean**: Expected value (recommended for planning)
- **Pessimistic Mean**: Conservative estimate
- **Activity Rate**: % of historical days that were non-zero

## Why This Is More Accurate

1. **Separates concerns**: On/off probability vs. trend
2. **Respects data structure**: Recognizes categorical nature
3. **Interpretable**: Each scenario has clear business meaning
4. **Range of outcomes**: Shows what could happen under different conditions
5. **Not over-compressed**: Realistic scenario isn't artificially small

## Usage Recommendations

- **For planning:** Use **Realistic** forecast mean
- **For risk assessment:** Use **Pessimistic** forecast mean
- **For optimization:** Use **Optimistic** to see potential
- **For accuracy:** The realistic scenario should align with your domain knowledge about product availability

## Technical Details

### Activity Probability Calculation
```python
active_probability = (non_zero_days / total_days)
# Example: 700 active days / 1000 total = 0.70 activity rate
```

### Model Parameters
- Uses only non-zero values for Prophet training
- Conservative changepoint detection (changepoint_prior_scale=0.01)
- No negative predictions (clipped to 0)
- 95% confidence intervals

### When Model Fails
- **Cherry** (100% zeros): No forecast possible → shows error
- **Fruits with <10 non-zero points**: Not enough data → shows error

