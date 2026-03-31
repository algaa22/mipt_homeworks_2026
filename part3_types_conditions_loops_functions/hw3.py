#!/usr/bin/env python

from typing import Any

UNKNOWN_COMMAND_MSG = "Unknown command!"
NONPOSITIVE_VALUE_MSG = "Value must be greater than zero!"
INCORRECT_DATE_MSG = "Invalid date!"
NOT_EXISTS_CATEGORY = "Category not exists!"
OP_SUCCESS_MSG = "Added"

EXPENSE_CATEGORIES = {
    "Food": ("Supermarket", "Restaurants", "FastFood", "Coffee", "Delivery"),
    "Transport": ("Taxi", "Public transport", "Gas", "Car service"),
    "Housing": ("Rent", "Utilities", "Repairs", "Furniture"),
    "Health": ("Pharmacy", "Doctors", "Dentist", "Lab tests"),
    "Entertainment": ("Movies", "Concerts", "Games", "Subscriptions"),
    "Clothing": ("Outerwear", "Casual", "Shoes", "Accessories"),
    "Education": ("Courses", "Books", "Tutors"),
    "Communications": ("Mobile", "Internet", "Subscriptions"),
    "Other": ("SomeCategory", "SomeOtherCategory"),
}

financial_transactions_storage: list[dict[str, Any]] = []
DATE_PARTS = 3
MAX_MONTH = 12
MOUTH_FEB = 2
FLOAT_PARTS = 2
CATEGORY_PARTS = 2
INCOME_ARGS = 3
COST_ARGS = 4
STATS_ARGS = 2
CATEGORIES_COMMAND_ARGS = 2


def is_leap_year(year: int) -> bool:
    four = year % 4 == 0
    hundred = year % 100 == 0
    four_hundred = year % 400 == 0
    return (four and not hundred) or four_hundred


def extract_date(maybe_dt: str) -> tuple[int, int, int] | None:
    parts = maybe_dt.split("-")
    if len(parts) != DATE_PARTS:
        return None

    for part in parts:
        if not part.isdigit():
            return None

    day, month, year = int(parts[0]), int(parts[1]), int(parts[2])
    if year < 1 or month < 1 or month > MAX_MONTH or day < 1:
        return None

    days_in_month = [31, 28, 31, 30, 31, 30, 31, 31, 30, 31, 30, 31]
    if month == MOUTH_FEB and is_leap_year(year):
        days_in_month[1] = 29

    if day > days_in_month[month - 1]:
        return None

    return (day, month, year)


def parse_amount(amount_input: str) -> float | None:
    amount = amount_input.replace(",", ".")

    for i, char in enumerate(amount):
        if i == 0 and char == "-":
            continue
        if char != "." and not char.isdigit():
            return None
    if amount.count(".") > 1:
        return None

    if "." in amount:
        parts = amount.split(".")
        if len(parts) != FLOAT_PARTS or not parts[0] or not parts[1]:
            return None
        if not parts[1].isdigit():
            return None
    return float(amount)


def parse_category(category_str: str) -> tuple[str, str] | None:
    if "::" not in category_str:
        return None

    parts = category_str.split("::")
    if len(parts) != CATEGORY_PARTS:
        return None

    common_category, target_category = parts
    if not common_category or not target_category:
        return None

    return common_category, target_category


def find_category(common_category: str, target_category: str) -> bool:
    if common_category not in EXPENSE_CATEGORIES:
        return False

    return target_category in EXPENSE_CATEGORIES[common_category]


def cost_categories_handler() -> str:
    result = []
    for category, subcategories in EXPENSE_CATEGORIES.items():
        result.extend(f"{category}::{subcategory}" for subcategory in subcategories)
    return "\n".join(result)


def income_handler(amount: float, income_date: str) -> str:
    if amount <= 0:
        financial_transactions_storage.append({})
        return NONPOSITIVE_VALUE_MSG

    date_tuple = extract_date(income_date)
    if date_tuple is None:
        financial_transactions_storage.append({})
        return INCORRECT_DATE_MSG

    financial_transactions_storage.append({
        "type": "income",
        "amount": amount,
        "date": date_tuple
    })
    return OP_SUCCESS_MSG


def cost_handler(category_name: str, amount: float, income_date: str) -> str:
    if amount <= 0:
        financial_transactions_storage.append({})
        return NONPOSITIVE_VALUE_MSG

    date_tuple = extract_date(income_date)
    if date_tuple is None:
        financial_transactions_storage.append({})
        return INCORRECT_DATE_MSG

    category_parts = parse_category(category_name)
    if category_parts is None:
        financial_transactions_storage.append({})
        return NOT_EXISTS_CATEGORY
    common_category, target_category = category_parts

    if not find_category(common_category, target_category):
        financial_transactions_storage.append({})
        return NOT_EXISTS_CATEGORY
    financial_transactions_storage.append({
        "type": "cost",
        "category": target_category,
        "parent_category": common_category,
        "amount": amount,
        "date": date_tuple
    })
    return OP_SUCCESS_MSG


def date_before_or_equal(
        transaction_date: tuple[int, int, int],
        stats_date: tuple[int, int, int]
) -> bool:
    day, month, year = transaction_date
    stats_day, stats_month, stats_year = stats_date

    if year < stats_year:
        return True
    if year > stats_year:
        return False
    if month < stats_month:
        return True
    if month > stats_month:
        return False
    return day <= stats_day


def date_in_month(
        transaction_date: tuple[int, int, int],
        stats_date: tuple[int, int, int]
) -> bool:
    day, month, year = transaction_date
    stats_day, stats_month, stats_year = stats_date
    return (year == stats_year and month == stats_month and day <= stats_day)


def calculate_capital(stats_date: tuple[int, int, int]) -> float:
    total_capital = 0.0

    for transaction in financial_transactions_storage:
        if not transaction:
            continue

        date_tuple = transaction.get("date")
        if date_tuple is None:
            continue

        if date_before_or_equal(date_tuple, stats_date):
            if transaction["type"] == "income":
                total_capital += transaction["amount"]
            elif transaction["type"] == "cost":
                total_capital -= transaction["amount"]

    return total_capital


def calculate_month_stat(stats_date: tuple[int, int, int]) -> tuple[float, dict[str, float]]:
    month_incomes = 0.0
    month_by_category: dict[str, float] = {}

    for transaction in financial_transactions_storage:
        if not transaction:
            continue

        date_tuple = transaction.get("date")
        if date_tuple is None:
            continue

        if date_in_month(date_tuple, stats_date):
            if transaction["type"] == "income":
                month_incomes += transaction["amount"]
            elif transaction["type"] == "cost":
                parent_category = transaction["parent_category"]
                month_by_category[parent_category] = (
                        month_by_category.get(parent_category, 0.0) + transaction["amount"]
                )

    return month_incomes, month_by_category


def stats_handler(report_date: str) -> str:
    date_tuple = extract_date(report_date)
    if date_tuple is None:
        return INCORRECT_DATE_MSG

    total_capital = calculate_capital(date_tuple)
    month_incomes, month_by_category = calculate_month_stat(date_tuple)

    month_total_costs = sum(month_by_category.values())
    month_result = month_incomes - month_total_costs

    result = []
    result.append(f"Your statistics as of {report_date}:")
    result.append(f"Total capital: {total_capital:.2f} rubles")

    if month_result >= 0:
        result.append(f"This month, the profit amounted to {month_result:.2f} rubles.")
    else:
        result.append(f"This month, the loss amounted to {abs(month_result):.2f} rubles.")

    result.append(f"Income: {month_incomes:.2f} rubles")
    result.append(f"Expenses: {month_total_costs:.2f} rubles")
    result.append("")

    if month_by_category:
        result.append("Details (category: amount):")
        sorted_categories = sorted(month_by_category.items())
        for i, (category, amount) in enumerate(sorted_categories, 1):
            if amount.is_integer():
                result.append(f"{i}. {category}: {int(amount)}")
            else:
                result.append(f"{i}. {category}: {amount}")
    else:
        result.append("Details (category: amount):")

    return "\n".join(result)


def process_income(parts: list[str]) -> str:
    if len(parts) != INCOME_ARGS:
        return UNKNOWN_COMMAND_MSG

    amount = parse_amount(parts[1])
    if amount is None or amount <= 0:
        return NONPOSITIVE_VALUE_MSG

    return income_handler(amount, parts[2])


def process_cost(parts: list[str]) -> str:
    if len(parts) == CATEGORIES_COMMAND_ARGS and parts[1] == "categories":
        return cost_categories_handler()

    if len(parts) != COST_ARGS:
        return UNKNOWN_COMMAND_MSG

    amount = parse_amount(parts[2])
    if amount is None or amount <= 0:
        return NONPOSITIVE_VALUE_MSG

    return cost_handler(parts[1], amount, parts[3])


def process_stats(parts: list[str]) -> str:
    if len(parts) != STATS_ARGS:
        return UNKNOWN_COMMAND_MSG

    return stats_handler(parts[1])


def main() -> None:
    while True:
        command_line = input().strip()
        if not command_line:
            break

        parts = command_line.split()
        command = parts[0]

        if command == "income":
            result = process_income(parts)
            print(result)
        elif command == "cost":
            result = process_cost(parts)
            print(result)
        elif command == "stats":
            result = process_stats(parts)
            print(result)
        else:
            print(UNKNOWN_COMMAND_MSG)


if __name__ == "__main__":
    main()
