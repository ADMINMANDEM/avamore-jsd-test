from flask import Flask, request, jsonify, render_template
from datetime import datetime, timedelta

app = Flask(__name__)

# Constants
BUILD_FUNDS = 250000
FACILITY_C = 25000
ARRANGEMENT_FREE = 5000
DEFAULT_INTEREST_RATE = 0.02
BUILD_DRAWDOWNS = [
    {"date": "14-Feb-23", "payment_amount": 25000},
    {"date": "25-Mar-23", "payment_amount": 25000},
    {"date": "03-May-23", "payment_amount": 25000},
    {"date": "11-Jun-23", "payment_amount": 25000},
    {"date": "20-Jul-23", "payment_amount": 25000},
    {"date": "28-Aug-23", "payment_amount": 25000},
    {"date": "06-Oct-23", "payment_amount": 25000},
    {"date": "14-Nov-23", "payment_amount": 25000},
    {"date": "23-Dec-23", "payment_amount": 25000},
    {"date": "31-Jan-24", "payment_amount": 25000}
]
CAPITAL_REPAYMENTS = [
    {"date": "23-Feb-24", "payment_amount": 100000}
]
DATE_OF_LOAN = "15-Jan-23"
REDEMPTION_STATEMENT_DATE = "23-Apr-24"

# Inital Calculations
interestRetention = FACILITY_C - ARRANGEMENT_FREE
impliedDailyDefaultRate = ((DEFAULT_INTEREST_RATE*100) / 30) / 100
dailyInterest = 0


@app.route('/')
def index():
    return render_template('index.html')

@app.route('/calculate_interest', methods=['POST'])
def calculate_interest():
    data = request.json
    landAdvance = float(data['landAdvance'])
    contractualMonthlyRate = float(data['contractualMonthlyRate'])
    defaultPeriodStart = datetime.strptime(data['defaultPeriodStart'], "%Y-%m-%d")
    defaultPeriodEnd = datetime.strptime(data['defaultPeriodEnd'], "%Y-%m-%d")

    openingPB = landAdvance + ARRANGEMENT_FREE
    impliedDailyRegRate = (contractualMonthlyRate / 30) / 100

    accruedInterest = calculate_for_dates(openingPB, DATE_OF_LOAN, REDEMPTION_STATEMENT_DATE, defaultPeriodStart, defaultPeriodEnd, impliedDailyRegRate)
    return jsonify({"accruedInterest": accruedInterest})

def calculate_daily_interest(openingPB, drawdown, currentInterestBalance, defaultOn, impliedDailyRegRate):
    if defaultOn:
        dailyInterest = (openingPB + drawdown + currentInterestBalance) * impliedDailyDefaultRate
    else:
        dailyInterest = (openingPB + drawdown + currentInterestBalance) * impliedDailyRegRate
    return dailyInterest

def calculate_for_dates(openingPB, startDate, endDate, defaultPeriodStart, defaultPeriodEnd, impliedDailyRegRate):
    startDate = datetime.strptime(startDate, "%d-%b-%y")
    endDate = datetime.strptime(endDate, "%d-%b-%y")

    dateList = [(startDate + timedelta(days=x)).date() for x in range((endDate - startDate).days + 1)]
    
    accruedDailyInterest = 0
    closingPB = openingPB
    currentInterestBalance = interestRetention

    for date in dateList:
        defaultOn = False
        if defaultPeriodStart.date() <= date <= defaultPeriodEnd.date():
            defaultOn = True

        if accruedDailyInterest >= currentInterestBalance:
            currentInterestBalance = accruedDailyInterest

        openingPB = closingPB
        todaysDrawdown = 0
        todaysCapitalRepayment = 0

        for drawdown in BUILD_DRAWDOWNS:
            if drawdown["date"] == date.strftime("%d-%b-%y"):
                todaysDrawdown = drawdown["payment_amount"]
        for capitalRepayment in CAPITAL_REPAYMENTS:
            if capitalRepayment["date"] == date.strftime("%d-%b-%y"):
                todaysCapitalRepayment = capitalRepayment["payment_amount"]

        dailyInterest = calculate_daily_interest(openingPB, todaysDrawdown, currentInterestBalance, defaultOn, impliedDailyRegRate)
        closingPB = openingPB + todaysDrawdown - todaysCapitalRepayment
        accruedDailyInterest += dailyInterest 
    
    return accruedDailyInterest

if __name__ == '__main__':
    app.run(debug=True)
