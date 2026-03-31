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
        if len(parts) != 2 or not parts[0] or not parts[1]:
            return None
        if not parts[1].isdigit():
            return None
    return float(amount)


def find_category(category_name: str) -> str | None:
    for parent_category, subcategories in EXPENSE_CATEGORIES.items():
        if category_name in subcategories:
            return parent_category
    return None


def cost_categories_handler() -> str:
    result = []
    for category, subcategories in EXPENSE_CATEGORIES.items():
        subcategories_str = ", ".join(subcategories)
        result.append(f"{category}: {subcategories_str}")
    return "\n".join(result)


def income_handler(amount: float, income_date: str) -> str:
    date_tuple = extract_date(income_date)
    if date_tuple is None:
        return INCORRECT_DATE_MSG

    financial_transactions_storage.append({
        "type": "income",
        "amount": amount,
        "date": income_date
    })
    return OP_SUCCESS_MSG


def cost_handler(category_name: str, amount: float, income_date: str) -> str:
    date_tuple = extract_date(income_date)
    if date_tuple is None:
        return INCORRECT_DATE_MSG

    if amount <= 0:
        return NONPOSITIVE_VALUE_MSG

    parent_category = find_category(category_name)
    if parent_category is None:
        return NOT_EXISTS_CATEGORY

    financial_transactions_storage.append({
        "type": "cost",
        "category": category_name,
        "parent_category": parent_category,
        "amount": amount,
        "date": income_date
    })
    return OP_SUCCESS_MSG


def date_before_or_equal(day: int, month: int, year: int,
                         stats_day: int, stats_month: int, stats_year: int) -> bool:
    if year < stats_year:
        return True
    if year > stats_year:
        return False
    if month < stats_month:
        return True
    if month > stats_month:
        return False
    return day <= stats_day


def date_in_month(day: int, month: int, year: int,
                  stats_day: int, stats_month: int, stats_year: int) -> bool:
    return (year == stats_year and month == stats_month and day <= stats_day)


def calculate_capital(stats_date: tuple[int, int, int]) -> float:
    total_capital = 0.0
    stats_day, stats_month, stats_year = stats_date

    for transaction in financial_transactions_storage:
        date_tuple = extract_date(transaction["date"])
        if date_tuple is None:
            continue
        day, month, year = date_tuple

        if date_before_or_equal(day, month, year, stats_day, stats_month, stats_year):
            if transaction["type"] == "income":
                total_capital += transaction["amount"]
            elif transaction["type"] == "cost":
                total_capital -= transaction["amount"]

    return total_capital


def calculate_month_stat(stats_date: tuple[int, int, int]) -> tuple[float, dict[str, float]]:
    month_incomes = 0.0
    month_by_category: dict[str, float] = {}
    stats_day, stats_month, stats_year = stats_date

    for transaction in financial_transactions_storage:
        date_tuple = extract_date(transaction["date"])
        if date_tuple is None:
            continue
        day, month, year = date_tuple

        if date_in_month(day, month, year, stats_day, stats_month, stats_year):
            if transaction["type"] == "income":
                month_incomes += transaction["amount"]
            elif transaction["type"] == "cost":
                parent_category = transaction["parent_category"]
                month_by_category[parent_category] = month_by_category.get(parent_category, 0.0) + transaction["amount"]

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
    result.append(f"Ваша статистика по состоянию на {report_date}:")
    result.append(f"Суммарный капитал: {total_capital:.2f} рублей")

    if month_result >= 0:
        result.append(f"В этом месяце прибыль составила {month_result:.2f} рублей")
    else:
        result.append(f"В этом месяце убыток составил {abs(month_result):.2f} рублей")

    result.append(f"Доходы: {month_incomes:.2f} рублей")
    result.append(f"Расходы: {month_total_costs:.2f} рублей")
    result.append("Детализация (категория: сумма):")

    if month_by_category:
        sorted_categories = sorted(month_by_category.items())
        for i, (category, amount) in enumerate(sorted_categories, 1):
            if amount.is_integer():
                result.append(f"{i}. {category}: {int(amount)}")
            else:
                result.append(f"{i}. {category}: {amount}")
    else:
        result.append("")

    return "\n".join(result)


def main() -> None:
    while True:
        try:
            command_line = input().strip()
        except EOFError:
            break

        if not command_line:
            continue

        parts = command_line.split()
        command = parts[0]

        if command == "income":
            if len(parts) != 3:
                print(UNKNOWN_COMMAND_MSG)
                continue

            amount = parse_amount(parts[1])
            if amount is None or amount <= 0:
                print(NONPOSITIVE_VALUE_MSG)
                continue

            result = income_handler(amount, parts[2])
            print(result)

        elif command == "cost":
            if len(parts) != 4:
                print(UNKNOWN_COMMAND_MSG)
                continue

            amount = parse_amount(parts[2])
            if amount is None:
                print(NONPOSITIVE_VALUE_MSG)
                continue

            result = cost_handler(parts[1], amount, parts[3])
            print(result)

        elif command == "categories":
            result = cost_categories_handler()
            print(result)

        elif command == "stats":
            if len(parts) != 2:
                print(UNKNOWN_COMMAND_MSG)
                continue

            result = stats_handler(parts[1])
            print(result)

        else:
            print(UNKNOWN_COMMAND_MSG)


if __name__ == "__main__":
    main()