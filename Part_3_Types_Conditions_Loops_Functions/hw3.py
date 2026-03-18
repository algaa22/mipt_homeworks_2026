#!/usr/bin/env python

UNKNOWN_COMMAND_MSG = "Unknown command!"
NONPOSITIVE_VALUE_MSG = "Value must be greater than zero!"
INCORRECT_DATE_MSG = "Invalid date!"
OP_SUCCESS_MSG = "Added"
DATE_PARTS = 3
MAX_MONTH = 12
INCOME_ARGS = 3
COST_ARGS = 4
STATS_ARGS = 2
FLOAT_PARTS = 2
MOUTH_FEB = 2
ZERO = 0.0

DateTuple = tuple[int, int, int]
IncomeRecord = tuple[float, DateTuple]
CostRecord = tuple[str, float, DateTuple]


def is_leap_year(year: int) -> bool:
    four = year % 4 == 0
    hundred = year % 100 == 0
    four_hundred = year % 400 == 0
    return (four and not hundred) or four_hundred

def extract_date(maybe_dt: str) -> DateTuple | None:
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


def income_handler(parts: list[str], incomes: list[IncomeRecord]) -> None:
    if len(parts) != INCOME_ARGS:
        print(UNKNOWN_COMMAND_MSG)
        return

    amount_input = parts[1]
    date = parts[2]

    amount = parse_amount(amount_input)
    if amount is None or amount <= 0:
        print(NONPOSITIVE_VALUE_MSG)
        return

    date_tuple = extract_date(date)
    if date_tuple is None:
        print(INCORRECT_DATE_MSG)
        return

    incomes.append((amount, date_tuple))
    print(OP_SUCCESS_MSG)


def cost_handler(parts: list[str], costs: list[CostRecord]) -> None:
    if len(parts) != COST_ARGS:
        print(UNKNOWN_COMMAND_MSG)
        return

    category = parts[1]
    amount_input = parts[2]
    date = parts[3]

    if not category or " " in category or "," in category or "." in category:
        print(UNKNOWN_COMMAND_MSG)
        return

    amount = parse_amount(amount_input)
    if amount is None or amount <= 0:
        print(NONPOSITIVE_VALUE_MSG)
        return

    date_tuple = extract_date(date)
    if date_tuple is None:
        print(INCORRECT_DATE_MSG)
        return

    costs.append((category, amount, date_tuple))
    print(OP_SUCCESS_MSG)

def date_before_or_equal( day: int, month: int, year: int,  # noqa: PLR0913
                             stats_day: int,
                             stats_month: int,
                             stats_year: int) -> bool:
    if year < stats_year or month < stats_month:
        return True
    if year > stats_year or month > stats_month:
        return False
    return day <= stats_day


def calculate_capital(
    incomes: list[IncomeRecord],
    costs: list[CostRecord],
    stats_day: int,
    stats_month: int,
    stats_year: int) -> float:
    total_capital = ZERO
    for amount, (day, month, year) in incomes:
        if date_before_or_equal(day, month, year, stats_day, stats_month, stats_year):
            total_capital += amount

    for _, amount, (day, month, year) in costs:
         if date_before_or_equal(day, month, year, stats_day, stats_month, stats_year):
            total_capital -= amount
    return total_capital

def date_in_month( day: int, month: int, year: int,  # noqa: PLR0913
    stats_day: int, stats_month: int, stats_year: int) -> bool:
    return (year == stats_year and month == stats_month and day <= stats_day)

def calculate_month_stat(
    incomes: list[IncomeRecord],
    costs: list[CostRecord],
    stats_day: int,
    stats_month: int,
    stats_year: int) -> tuple[float, dict[str, float]]:
    month_incomes = ZERO
    month_by_category: dict[str, float] = {}

    for amount, (day, month, year) in incomes:
        if date_in_month(day, month, year, stats_day, stats_month, stats_year):
            month_incomes += amount

    for category, amount, (day, month, year) in costs:
        if date_in_month(day, month, year, stats_day, stats_month, stats_year):
            month_by_category[category] = month_by_category.get(category, ZERO) + amount
    return month_incomes, month_by_category

def print_stats(  # noqa: PLR0913
    date: str,
    total_capital: float,
    month_incomes: float,
    month_total_costs: float,
    month_result: float,
    month_by_category: dict[str, float]
) -> None:
    print(f"Ваша статистика по состоянию на {date}:")
    print(f"Суммарный капитал: {total_capital:.2f} рублей")

    if month_result >= 0:
        print(f"В этом месяце прибыль составила {month_result:.2f} рублей")  # noqa: RUF001
    else:
        print(f"В этом месяце убыток составил {abs(month_result):.2f} рублей")  # noqa: RUF001

    print(f"Доходы: {month_incomes:.2f} рублей")
    print(f"Расходы: {month_total_costs:.2f} рублей")
    print("Детализация (категория: сумма):")

    if month_by_category:
        sorted_categories = sorted(month_by_category.items())
        for i, (category, amount) in enumerate(sorted_categories, 1):
            if amount.is_integer():
                print(f"{i}. {category}: {int(amount)}")
            else:
                print(f"{i}. {category}: {amount}")
    else:
        print()


def stats_handler(
    parts: list[str],
    incomes: list[IncomeRecord],
    costs: list[CostRecord]) -> None:
    if len(parts) != STATS_ARGS:
        print(UNKNOWN_COMMAND_MSG)
        return

    date = parts[1]
    date_tuple = extract_date(date)
    if date_tuple is None:
        print(INCORRECT_DATE_MSG)
        return

    stats_day, stats_month, stats_year = date_tuple
    total_capital = calculate_capital(incomes, costs, stats_day, stats_month, stats_year)
    month_incomes, month_by_category = calculate_month_stat(
        incomes, costs, stats_day, stats_month, stats_year
    )

    month_total_costs = sum(month_by_category.values())
    month_result = month_incomes - month_total_costs

    print_stats(
        date, total_capital, month_incomes,
        month_total_costs, month_result, month_by_category
    )


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


def main() -> None:
    incomes: list[IncomeRecord] = []
    costs: list[CostRecord] = []

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
            income_handler(parts, incomes)
        elif command == "cost":
            cost_handler(parts, costs)
        elif command == "stats":
            stats_handler(parts, incomes, costs)
        else:
            print(UNKNOWN_COMMAND_MSG)

if __name__ == "__main__":
    main()
