import datetime

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

# Error Handling
def input_float(prompt, error_message="Invalid input. Please enter a valid number."):
    while True:
        value = input(prompt)
        try:
            # Remove the '%' sign if present
            if value.endswith('%'):
                value = value[:-1]
            # Convert the input string to a float
            return float(value)
        except ValueError:
            print(error_message)


def input_date(prompt, date_format="%d-%b-%y"):
    while True:
        date_str = input(prompt)
        try:
            return datetime.datetime.strptime(date_str, date_format)
        except ValueError:
            print(f"Invalid date format. Please enter the date in the format {date_format}.")

# Inputs
landAdvance = input_float("Please enter Facility A (Land Advance): ")
contractualMonthlyRate = input_float("Please enter Contractual Monthly Rate (%pm): ")
defaultPeriodStart = input_date("Please enter Beginning of Default Period in the format DD-MMM-YYYY: ")

# Checks end date is after start date
while True:
    defaultPeriodEnd = input_date("Please enter End of Default Period in the format DD-MMM-YYYY: ")
    if defaultPeriodStart > defaultPeriodEnd:
        print("End date must be after start date")
    else:
        break

# Inital Calculations
interestRetention = FACILITY_C - ARRANGEMENT_FREE
impliedDailyRegRate = (contractualMonthlyRate / 30) / 100
impliedRegAnnualRate = (1 + impliedDailyRegRate)**365 - 1
impliedDailyDefaultRate = ((DEFAULT_INTEREST_RATE*100) / 30) / 100
dailyInterest = 0
openingPB = landAdvance + ARRANGEMENT_FREE

# Function calculates the interest on a given day
def calculate_daily_interest(openingPB, drawdown, currentInterestBalance, defaultOn):
    if defaultOn == True:
        dailyInterest = (openingPB + drawdown + currentInterestBalance) * impliedDailyDefaultRate
    else:
        dailyInterest = (openingPB + drawdown + currentInterestBalance) * impliedDailyRegRate
    return dailyInterest

# Calculates the accrued interest on the date constants
def calculate_for_dates(openingPB, startDate, endDate):
    # Convert date constants strings to datetime objects
    startDate = datetime.datetime.strptime(startDate, "%d-%b-%y")
    endDate = datetime.datetime.strptime(endDate, "%d-%b-%y")
    
    # Generates a list of dates between startDate and endDate
    dateList = [(startDate + datetime.timedelta(days=x)).date() for x in range((endDate - startDate).days + 1)]
    
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
        # Checks if there's a drawdown for this date
        for drawdown in BUILD_DRAWDOWNS:
            if drawdown["date"] == date.strftime("%d-%b-%y"):
                todaysDrawdown = drawdown["payment_amount"]
        for capitalRepayment in CAPITAL_REPAYMENTS:
            if capitalRepayment["date"] == date.strftime("%d-%b-%y"):
                todaysCapitalRepayment = capitalRepayment["payment_amount"]

        dailyInterest = calculate_daily_interest(openingPB, todaysDrawdown, currentInterestBalance, defaultOn)
        closingPB = openingPB + todaysDrawdown - todaysCapitalRepayment
        accruedDailyInterest += dailyInterest 
        
    
    return accruedDailyInterest

accruedInterest = calculate_for_dates(openingPB, DATE_OF_LOAN, REDEMPTION_STATEMENT_DATE)
print("Total Interest Due: ", accruedInterest)
