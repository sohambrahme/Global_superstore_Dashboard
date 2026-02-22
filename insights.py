from typing import List, Dict
import pandas as pd

def generate_insights(df: pd.DataFrame) -> List[str]:
    """Generates business insights based on the given dataframe."""
    insights = []
    
    if df.empty:
        return ["No data available for the current filters."]
        
    total_sales = df['Sales'].sum()
    total_profit = df['Profit'].sum()
    
    # 1. Overall Profitability
    if total_sales > 0:
        profit_margin = (total_profit / total_sales) * 100
        if profit_margin > 15:
            insights.append(f"🟢 **Healthy Profit Margin:** The overall profit margin is strong at **{profit_margin:.1f}%** for the selected data.")
        elif profit_margin > 0:
            insights.append(f"🟡 **Moderate Profitability:** The profit margin is at **{profit_margin:.1f}%**. Consider reviewing discount strategies.")
        else:
            insights.append(f"🔴 **Loss Warning:** The selected segment is operating at a net loss (Margin: **{profit_margin:.1f}%**). Investigate highest discounting or shipping costs.")

    # 2. Top Performing Category by Profit
    if 'Category' in df.columns:
        cat_profit = df.groupby('Category')['Profit'].sum().sort_values(ascending=False)
        top_cat = cat_profit.index[0]
        bottom_cat = cat_profit.index[-1]
        
        if len(cat_profit) > 1:
            insights.append(f"🌟 **Category Performance:** **{top_cat}** is the most profitable category, whereas **{bottom_cat}** generates the least profit.")
            
    # 3. Discount Impact
    avg_discount = df['Discount'].mean()
    if avg_discount > 0.3: # Threshold of 30% average discount
         insights.append(f"⚠️ **High Discount Alert:** The average discount applied is quite high (**{avg_discount:.1%}**). This may be severely impacting absolute profits.")
    elif avg_discount < 0.1:
         insights.append(f"✅ **Healthy Pricing:** Discounts are kept low on average (**{avg_discount:.1%}**), preserving profit margins.")
         
    # 4. Quantity vs Profit Correlation check
    highest_qty_item = df.groupby('Sub-Category')['Quantity'].sum().idxmax()
    profit_of_highest_qty = df[df['Sub-Category'] == highest_qty_item]['Profit'].sum()
    
    if profit_of_highest_qty < 0:
         insights.append(f"🚨 **Volume vs Value Mismatch:** **{highest_qty_item}** has the highest sales volume but is currently yielding a **negative profit**. A pricing or cost review is highly recommended.")
    else:
        insights.append(f"📦 **Top Volume Driver:** **{highest_qty_item}** moves the most units, contributing positively to profit.")

    return insights
