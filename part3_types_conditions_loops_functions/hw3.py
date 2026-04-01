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
TRANSACTION_TYPE = "type"
TRANSACTION_INCOME = "income"
TRANSACTION_COST = "cost"
AMOUNT_KEY = "amount"
DATE_KEY = "date"
CATEGORY_KEY = "category"
PARENT_CATEGORY_KEY = "parent_category"


def is_leap_year(year: int) -> bool:
    four = year % 4 == 0
    hundred = year % 100 == 0
    four_hundred = year % 400 == 0
    return (four and not hundred) or four_hundred


def split_date_parts(maybe_dt: str) -> list[str] | None:
    parts = maybe_dt.split("-")
    if len(parts) != DATE_PARTS:
        return None
    return parts


def parse_date_numbers(date_parts: list[str]) -> tuple[int, int, int] | None:
    for part in date_parts:
        if not part.isdigit():
            return None

    day = int(date_parts[0])
    month = int(date_parts[1])
    year = int(date_parts[2])
    return day, month, year


def get_days_in_month(year: int, month: int) -> int:
    days_in_month = [31, 28, 31, 30, 31, 30, 31, 31, 30, 31, 30, 31]
    if month == MOUTH_FEB and is_leap_year(year):
        return 29
    return days_in_month[month - 1]


def is_valid_date(day: int, month: int, year: int) -> bool:
    if year < 1 or month < 1 or month > MAX_MONTH or day < 1:
        return False
    max_day = get_days_in_month(year, month)
    return day <= max_day


def extract_date(maybe_dt: str) -> tuple[int, int, int] | None:
    date_parts = split_date_parts(maybe_dt)
    if date_parts is None:
        return None

    parsed_numbers = parse_date_numbers(date_parts)
    if parsed_numbers is None:
        return None

    day, month, year = parsed_numbers
    if not is_valid_date(day, month, year):
        return None

    return day, month, year


def is_normal_number(number_part: str) -> bool:
    return number_part.isdigit()


def check_digits_and_dots(amount: str) -> bool:
    for i, char in enumerate(amount):
        if i == 0 and char == "-":
            continue
        if char != "." and not char.isdigit():
            return False
    return True


def check_decimal_part(amount: str) -> bool:
    if amount.count(".") > 1:
        return False

    if "." in amount:
        parts = amount.split(".")
        if len(parts) != FLOAT_PARTS:
            return False
        if not parts[0] or not parts[1]:
            return False
        if not parts[1].isdigit():
            return False
    return True


def check_amount_format(amount: str) -> bool:
    return check_digits_and_dots(amount) and check_decimal_part(amount)


def parse_amount_parts(amount_input: str) -> tuple[float | None, bool]:
    amount = amount_input.replace(",", ".")

    if not check_amount_format(amount):
        return None, False

    if amount in ("", "-"):
        return None, False

    return float(amount), True


def parse_amount(amount_input: str) -> float | None:
    result, success = parse_amount_parts(amount_input)
    return result if success else None


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
    result: list[str] = []
    for category, subcategories in EXPENSE_CATEGORIES.items():
        result.extend(f"{category}::{subcategory}" for subcategory in subcategories)
    return "\n".join(result)


def create_income_transaction(
    amount: float,
    date_tuple: tuple[int, int, int],
) -> dict[str, Any]:
    return {
        TRANSACTION_TYPE: TRANSACTION_INCOME,
        AMOUNT_KEY: amount,
        DATE_KEY: date_tuple,
    }


def create_cost_transaction(
    category: str,
    parent_category: str,
    amount: float,
    date_tuple: tuple[int, int, int],
) -> dict[str, Any]:
    return {
        TRANSACTION_TYPE: TRANSACTION_COST,
        CATEGORY_KEY: category,
        PARENT_CATEGORY_KEY: parent_category,
        AMOUNT_KEY: amount,
        DATE_KEY: date_tuple,
    }


def income_handler(amount: float, income_date: str) -> str:
    if amount <= 0:
        financial_transactions_storage.append({})
        return NONPOSITIVE_VALUE_MSG

    date_tuple = extract_date(income_date)
    if date_tuple is None:
        financial_transactions_storage.append({})
        return INCORRECT_DATE_MSG

    transaction = create_income_transaction(amount, date_tuple)
    financial_transactions_storage.append(transaction)
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

    transaction = create_cost_transaction(target_category, common_category, amount, date_tuple)
    financial_transactions_storage.append(transaction)
    return OP_SUCCESS_MSG


def date_before_or_equal(
    trans_date: tuple[int, int, int],
    stats_date: tuple[int, int, int],
) -> bool:
    trans_day, trans_month, trans_year = trans_date
    stats_day, stats_month, stats_year = stats_date

    if trans_year < stats_year:
        return True
    if trans_year > stats_year:
        return False
    if trans_month < stats_month:
        return True
    if trans_month > stats_month:
        return False
    return trans_day <= stats_day


def date_in_month(
    trans_date: tuple[int, int, int],
    stats_date: tuple[int, int, int],
) -> bool:
    trans_day, trans_month, trans_year = trans_date
    stats_day, stats_month, stats_year = stats_date
    return trans_year == stats_year and trans_month == stats_month and trans_day <= stats_day


def get_transaction_date(transaction: dict[str, Any]) -> tuple[int, int, int] | None:
    date_value = transaction.get(DATE_KEY)
    if isinstance(date_value, tuple):
        return date_value
    return None


def process_transaction_for_total(
    transaction: dict[str, Any],
    stats_date: tuple[int, int, int],
    total: float,
) -> float:
    if not transaction:
        return total

    date_tuple = get_transaction_date(transaction)
    if date_tuple is None:
        return total

    day, month, year = date_tuple
    stats_day, stats_month, stats_year = stats_date

    trans_date = (day, month, year)
    stats_date_tuple = (stats_day, stats_month, stats_year)
    if not date_before_or_equal(trans_date, stats_date_tuple):
        return total

    amount = transaction.get(AMOUNT_KEY, 0)
    amount_value = float(amount)

    if transaction.get(TRANSACTION_TYPE) == TRANSACTION_INCOME:
        return total + amount_value
    return total - amount_value


def calculate_capital(stats_date: tuple[int, int, int]) -> float:
    total: float = 0
    for transaction in financial_transactions_storage:
        total = process_transaction_for_total(transaction, stats_date, total)
    return float(total)


def process_transaction_for_month(
    transaction: dict[str, Any],
    stats_date: tuple[int, int, int],
    month_income: float,
    month_expenses: float,
    category_stats: dict[str, float],
) -> tuple[float, float]:
    if not transaction:
        return month_income, month_expenses

    date_tuple = get_transaction_date(transaction)
    if date_tuple is None:
        return month_income, month_expenses

    day, month, year = date_tuple
    stats_day, stats_month, stats_year = stats_date

    trans_date = (day, month, year)
    stats_date_tuple = (stats_day, stats_month, stats_year)
    if not date_before_or_equal(trans_date, stats_date_tuple):
        return month_income, month_expenses

    if transaction.get(TRANSACTION_TYPE) == TRANSACTION_INCOME:
        return month_income + transaction.get(AMOUNT_KEY, 0), month_expenses

    amount = transaction.get(AMOUNT_KEY, 0)
    parent_category = transaction.get(PARENT_CATEGORY_KEY, "Other")
    current = category_stats.get(parent_category, 0)
    category_stats[parent_category] = current + amount
    return month_income, month_expenses + amount


def calculate_month_stat(stats_date: tuple[int, int, int]) -> tuple[float, dict[str, float]]:
    month_income: float = 0
    month_expenses: float = 0
    category_stats: dict[str, float] = {}

    for transaction in financial_transactions_storage:
        month_income, month_expenses = process_transaction_for_month(
            transaction, stats_date, month_income, month_expenses, category_stats
        )

    return float(month_income), category_stats


def _build_stats_lines(
    report_date: str,
    total_capital: float,
    month_income: float,
    month_expenses: float,
) -> list[str]:
    lines = [
        f"Your statistics as of {report_date}:",
        f"Total capital: {total_capital:.2f} rubles",
    ]

    month_result = month_income - month_expenses
    if month_result >= 0:
        lines.append(f"This month, the profit amounted to {month_result:.2f} rubles.")
    else:
        loss = abs(month_result)
        lines.append(f"This month, the loss amounted to {loss:.2f} rubles.")

    lines.append(f"Income: {month_income:.2f} rubles")
    lines.append(f"Expenses: {month_expenses:.2f} rubles")
    lines.append("")
    return lines


def _build_category_lines(category_stats: dict[str, float]) -> list[str]:
    if not category_stats:
        return ["Details (category: amount):"]

    lines = ["Details (category: amount):"]
    sorted_categories = sorted(category_stats.items())
    for idx, (category, amount) in enumerate(sorted_categories, 1):
        if amount.is_integer():
            lines.append(f"{idx}. {category}: {int(amount)}")
        else:
            lines.append(f"{idx}. {category}: {amount}")
    return lines


def format_stats_output(
    report_date: str,
    total_capital: float,
    month_income: float,
    month_expenses: float,
    category_stats: dict[str, float],
) -> str:
    lines = _build_stats_lines(report_date, total_capital, month_income, month_expenses)
    lines.extend(_build_category_lines(category_stats))
    return "\n".join(lines)


def stats_handler(report_date: str) -> str:
    date_tuple = extract_date(report_date)
    if date_tuple is None:
        return INCORRECT_DATE_MSG

    total_capital = calculate_capital(date_tuple)
    month_income, category_stats = calculate_month_stat(date_tuple)
    month_expenses = sum(category_stats.values())

    return format_stats_output(report_date, total_capital, month_income, month_expenses, category_stats)


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


def _process_command(parts: list[str]) -> str:
    if not parts:
        return UNKNOWN_COMMAND_MSG

    command = parts[0]
    if command == "income":
        return process_income(parts)
    if command == "cost":
        return process_cost(parts)
    if command == "stats":
        return process_stats(parts)
    return UNKNOWN_COMMAND_MSG


def main() -> None:
    while True:
        command_line = input().strip()
        if not command_line:
            break

        parts = command_line.split()
        result = _process_command(parts)
        print(result)


if __name__ == "__main__":
    main()
