from utils import get_final_df
from chart import create_chart

if __name__ == "__main__":
    df = get_final_df()
    create_chart(df)