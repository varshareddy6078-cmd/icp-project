
from flask import Flask, render_template, request, redirect, url_for
from datetime import datetime

app = Flask(__name__)

# Temporary storage
expenses = []
next_id = 1


# Home page and OR search
@app.route("/")
def home():
    global expenses

    category = request.args.get("category", "").strip()
    search_date = request.args.get("search_date", "").strip()
    search_month = request.args.get("search_month", "").strip()
    search_year = request.args.get("search_year", "").strip()
    amount_filter = request.args.get("amount_filter", "all")

    try:
        min_amount = float(request.args.get("min_amount") or 0)
    except ValueError:
        min_amount = 0

    try:
        max_amount = float(request.args.get("max_amount") or 0)
    except ValueError:
        max_amount = 0

    # Check which filters the user selected
    valid_year = search_year.isdigit() and len(search_year) == 4

    filters_used = any([
        category,
        search_date,
        search_month,
        valid_year,
        amount_filter != "all"
    ])

    filtered_expenses = []

    for e in expenses:
        matches = []

        # Category search
        if category:
            matches.append(
                category.lower() in e["category"].lower()
            )

        # Specific date search
        if search_date:
            matches.append(e["date"] == search_date)

        # Month search
        if search_month:
            matches.append(e["date"].startswith(search_month))

        # Year search
        if valid_year:
            matches.append(e["date"].startswith(search_year + "-"))

        # Amount filters
        if amount_filter == "200_300":
            matches.append(200 <= e["amount"] <= 300)

        elif amount_filter == "above_500":
            matches.append(e["amount"] > 500)

        elif amount_filter == "above_1000":
            matches.append(e["amount"] > 1000)

        elif amount_filter == "custom_between":
            matches.append(
                min_amount <= max_amount
                and min_amount <= e["amount"] <= max_amount
            )

        elif amount_filter == "custom_above":
            matches.append(e["amount"] > min_amount)

        elif amount_filter == "custom_below":
            matches.append(e["amount"] < min_amount)

        # OR: include if at least one condition matches
        if not filters_used or any(matches):
            filtered_expenses.append(e)

    # Show newest expenses first
    filtered_expenses.sort(
        key=lambda e: (e["date"], e["id"]),
        reverse=True
    )

    # Calculate totals
    total = sum(e["amount"] for e in expenses)
    filtered_total = sum(e["amount"] for e in filtered_expenses)

    return render_template(
        "index.html",
        expenses=filtered_expenses,
        total=total,
        filtered_total=filtered_total,
        category=category,
        search_date=search_date,
        search_month=search_month,
        search_year=search_year,
        amount_filter=amount_filter,
        min_amount=request.args.get("min_amount", ""),
        max_amount=request.args.get("max_amount", "")
    )


# Add expense
@app.route("/add", methods=["POST"])
def add_expense():
    global next_id

    title = request.form.get("title", "").strip()
    category = request.form.get("category", "").strip()
    date = request.form.get("date", "").strip()

    try:
        amount = float(request.form.get("amount", 0))
    except (ValueError, TypeError):
        return "Please enter a valid amount.", 400

    try:
        datetime.strptime(date, "%Y-%m-%d")
    except ValueError:
        return "Please enter a valid date.", 400

    if not title or not category or amount <= 0:
        return "Please enter valid expense details.", 400

    expenses.append({
        "id": next_id,
        "title": title,
        "category": category,
        "amount": amount,
        "date": date
    })

    next_id += 1

    return redirect(url_for("home"))


# Delete expense
@app.route("/delete/<int:expense_id>", methods=["POST"])
def delete_expense(expense_id):
    expenses[:] = [
        e for e in expenses
        if e["id"] != expense_id
    ]

    return redirect(url_for("home"))


if __name__ == "__main__":
    app.run(debug=True)
