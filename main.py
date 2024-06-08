import json
import numpy as np
import pandas as pd
import streamlit as st
import plotly.express as px
from configuration import configure, PAGE_TITLE

# ! GLOBAL VARIABLES

GREEN = "#43aa8b"
RED = "#f94144"
INVESTMENT_IBAN = open("data/investment_iban", "r").read()
# ! FUNCTIONS


def upload_new_csv():
    # files: list = st.file_uploader(
    #     "Upload your csv", type="csv", accept_multiple_files=True
    # )

    # for file in files:
    #     file_content = file.getvalue().decode("utf-8")
    #     lines = file_content.split("\n")
    #     starting_balance = float(lines[5].split(";")[-2].replace(",", "."))
    #     last_balance = float(lines[-2].split(";")[-2].replace(",", "."))

    #     st.session_state["starting_balance"] = starting_balance
    #     st.session_state["last_balance"] = last_balance

    #     new_file_content = "\n".join(lines[7:-2])
    #     new_file_content = (
    #         new_file_content.replace(";", "%%%%").replace(",", ".").replace("%%%%", ",")
    #     )
    #     with open("data/file.csv", "w") as f:
    #         f.write(new_file_content)
    pass


def metrics():
    income = df["Change"][df["Change"] > 0].sum().round(2)
    expenses = abs(df["Change"][df["Change"] < 0].sum().round(2))
    investments = abs(df["Change"][df["IBAN"] == INVESTMENT_IBAN].sum().round(2))
    col1, col2, col3 = st.columns(3)
    col1.container(border=True).metric("📈 Income", income)
    col2.container(border=True).metric("📉 Expenses", expenses - investments)
    col3.container(border=True).metric("🌱 Investment", investments)


def balances() -> tuple[float, float]:
    with open("data/numbers.json") as f:
        numbers = json.load(f)
    return numbers["first_balance"], numbers["last_balance"]


def get_df() -> pd.DataFrame:

    df = pd.read_csv("data/file.csv", sep=",")
    # drop not needed columns
    df = df.drop(
        columns=[
            "Wert",
            "Fremde Gebühren",
            "Abweichender Empfänger",
            "Anzahl der Aufträge",
            "Anzahl der Schecks",
            "Soll",
            "Haben",
            "Kundenreferenz",
            "Mandatsreferenz",
            "Gläubiger ID",
            "BIC",
        ]
    )
    # rename columns
    df = df.rename(
        columns={
            "Buchungstag": "Date",
            "Betrag": "Change",
            "Umsatzart": "Type",
            "Begünstigter / Auftraggeber": "Person",
            "Verwendungszweck": "Purpose",
            "IBAN / Kontonummer": "IBAN",
            "Währung": "Currency",
        }
    )
    # format the date
    df["Date"] = pd.to_datetime(df["Date"], dayfirst=True)
    # format the change
    df["Change"] = df["Change"].astype(float)

    df = df.sort_values(by="Date")
    df = df.reset_index(drop=True)
    return df


def balance_over_time() -> None:

    df_daily["Balance_smooth"] = df_daily["Balance"].rolling(window=7).mean()
    balance_over_time_fig = px.line(
        df_daily, x="Date", y="Balance_smooth", title="Balance Over Time"
    )
    st.plotly_chart(balance_over_time_fig, use_container_width=True)


def changes_per_day() -> None:
    income_fig = px.bar(
        df_daily,
        x="Date",
        y="Change",
        color="Is_income",
        color_discrete_map={True: GREEN, False: RED},
        title="Changes per day",
    )
    st.plotly_chart(income_fig)


def changes_per_week() -> None:
    df_weekly_income = (
        df[df["Change"] > 0].resample("W", on="Date")["Change"].sum().reset_index()
    )
    df_weekly_expenses = (
        df[df["Change"] < 0].resample("W", on="Date")["Change"].sum().reset_index()
    )

    df_weekly_income.rename(columns={"Change": "Income"}, inplace=True)
    df_weekly_expenses.rename(columns={"Change": "Expenses"}, inplace=True)

    df_weekly = df_weekly_income.merge(df_weekly_expenses, on="Date")

    income_fig = px.bar(
        df_weekly,
        x="Date",
        y=["Income", "Expenses"],
        barmode="group",
        color_discrete_map={"Income": GREEN, "Expenses": RED},
        title="Income and Expenses per Week",
    )
    st.plotly_chart(income_fig)


def changes_per_month() -> None:
    df_monthly_income = (
        df[df["Change"] > 0].resample("M", on="Date")["Change"].sum().reset_index()
    )
    df_monthly_expenses = (
        df[df["Change"] < 0]
        .resample("M", on="Date")["Change"]
        .sum()
        .abs()
        .reset_index()
    )

    df_monthly_income.rename(columns={"Change": "Income"}, inplace=True)
    df_monthly_expenses.rename(columns={"Change": "Expenses"}, inplace=True)

    df_monthly = df_monthly_income.merge(df_monthly_expenses, on="Date")

    income_fig = px.bar(
        df_monthly,
        x="Date",
        y=["Income", "Expenses"],
        barmode="group",
        color_discrete_map={"Income": GREEN, "Expenses": RED},
        title="Income and Expenses per Month",
    )
    st.plotly_chart(income_fig)


def count_of_types() -> None:
    type_fig = px.histogram(
        df,
        x="Type",
        category_orders={"Type": df["Type"].value_counts().index},
        title="Count of Types",
    )
    st.plotly_chart(type_fig)


def changes_per_person() -> None:

    change_sum_threshhold = st.slider(
        "Threshhold in Euros", min_value=0, max_value=1000
    )
    change_sum_per_person = df.groupby("Person")["Change"].sum().reset_index()
    change_sum_per_person = change_sum_per_person[
        (change_sum_per_person["Change"] <= -change_sum_threshhold)
        | (change_sum_per_person["Change"] >= change_sum_threshhold)
    ]
    change_sum_per_person = change_sum_per_person.sort_values("Change", ascending=False)
    change_sum_per_person["Color"] = np.where(
        change_sum_per_person["Change"] > 0, "positive", "negative"
    )

    change_sum_per_person_fig = px.bar(
        change_sum_per_person,
        x="Person",
        y="Change",
        color="Color",
        color_discrete_map={"positive": GREEN, "negative": RED},
        title=f"Sum of Change per Person above or below {change_sum_threshhold} Euro",
    )
    st.plotly_chart(change_sum_per_person_fig)


# ! APP

configure()

st.title(PAGE_TITLE)


df = get_df()
first_balance, last_balance = balances()
df["Balance"] = first_balance + df["Change"].cumsum()
df["Is_income"] = df["Change"] > 0

df_daily = df.resample("h", on="Date")["Change"].sum().reset_index()
df_daily["Balance"] = first_balance + df_daily["Change"].cumsum()
df_daily["Is_income"] = df_daily["Change"] > 0

metrics()
with st.expander("Daten"):
    st.dataframe(df, use_container_width=True, hide_index=True)
balance_over_time()
changes_per = st.selectbox("Changes Per", options=["Day", "Week", "Month"])
if changes_per == "Day":
    changes_per_day()
elif changes_per == "Week":
    changes_per_week()
else:
    changes_per_month()


count_of_types()
changes_per_person()
