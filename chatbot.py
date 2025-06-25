import discord
from discord.ext import commands
import numpy as np
from sklearn.linear_model import LinearRegression
import json
import os
from datetime import datetime

# Bot configuration
TOKEN = 'YOUR_BOT_TOKEN_HERE'  # Replace with your bot token
PREFIX = '!'

# Initialize bot
intents = discord.Intents.default()
intents.message_content = True
bot = commands.Bot(command_prefix=PREFIX, intents=intents)

# Data storage file
DATA_FILE = 'gpa_data.json'

# Grade to GPA conversion
GRADE_TO_GPA = {
    'A+': 4.0, 'A': 4.0, 'A-': 3.7,
    'B+': 3.3, 'B': 3.0, 'B-': 2.7,
    'C+': 2.3, 'C': 2.0, 'C-': 1.7,
    'D+': 1.3, 'D': 1.0, 'D-': 0.7,
    'F': 0.0
}


class GPACalculator:
    @staticmethod
    def calculate_gpa(grades, credit_hours=None):
        """Calculate GPA from grades and optional credit hours"""
        if not grades:
            return 0.0

        if credit_hours and len(credit_hours) == len(grades):
            total_points = sum(g * h for g, h in zip(grades, credit_hours))
            total_hours = sum(credit_hours)
            return total_points / total_hours if total_hours > 0 else 0.0
        else:
            return sum(grades) / len(grades)

    @staticmethod
    def predict_gpa(historical_gpas):
        """Predict future GPA based on historical data"""
        if len(historical_gpas) < 2:
            return None

        # Create time series data
        X = np.array(range(len(historical_gpas))).reshape(-1, 1)
        y = np.array(historical_gpas)

        # Train linear regression model
        model = LinearRegression()
        model.fit(X, y)

        # Predict next semester's GPA
        next_semester = len(historical_gpas)
        prediction = model.predict([[next_semester]])[0]

        # Ensure prediction is within valid GPA range
        prediction = max(0.0, min(4.0, prediction))

        return prediction, model.coef_[0]  # Return prediction and trend


class UserData:
    def __init__(self):
        self.data = self.load_data()

    def load_data(self):
        """Load user data from file"""
        if os.path.exists(DATA_FILE):
            with open(DATA_FILE, 'r') as f:
                return json.load(f)
        return {}

    def save_data(self):
        """Save user data to file"""
        with open(DATA_FILE, 'w') as f:
            json.dump(self.data, f, indent=2)

    def get_user(self, user_id):
        """Get user data"""
        user_id = str(user_id)
        if user_id not in self.data:
            self.data[user_id] = {
                'gpas': [],
                'semesters': [],
                'current_grades': []
            }
        return self.data[user_id]

    def add_gpa(self, user_id, gpa, semester=None):
        """Add GPA record for user"""
        user = self.get_user(user_id)
        user['gpas'].append(gpa)
        if semester:
            user['semesters'].append(semester)
        else:
            user['semesters'].append(f"Semester {len(user['gpas'])}")
        self.save_data()


# Initialize user data
user_data = UserData()
gpa_calc = GPACalculator()


@bot.event
async def on_ready():
    print(f'{bot.user} has connected to Discord!')
    print(f'Bot is in {len(bot.guilds)} guilds')


@bot.command(name='help_gpa')
async def help_gpa(ctx):
    """Show help information"""
    embed = discord.Embed(
        title="📚 GPA Bot Commands",
        description="Calculate and predict your GPA!",
        color=discord.Color.blue()
    )

    commands_info = [
        ("!calculate", "Calculate GPA from grades\nUsage: `!calculate A B+ A- C+`"),
        ("!calculate_weighted", "Calculate weighted GPA\nUsage: `!calculate_weighted A,3 B+,4 A-,3`"),
        ("!add_gpa", "Add GPA to history\nUsage: `!add_gpa 3.5 Fall2023`"),
        ("!history", "View your GPA history"),
        ("!predict", "Predict your future GPA based on trends"),
        ("!clear", "Clear your GPA history"),
        ("!stats", "View detailed statistics")
    ]

    for cmd, desc in commands_info:
        embed.add_field(name=cmd, value=desc, inline=False)

    await ctx.send(embed=embed)


@bot.command(name='calculate')
async def calculate(ctx, *grades):
    """Calculate GPA from letter grades"""
    if not grades:
        await ctx.send("❌ Please provide grades! Example: `!calculate A B+ A- C+`")
        return

    try:
        # Convert letter grades to GPA values
        gpa_values = []
        for grade in grades:
            grade_upper = grade.upper()
            if grade_upper not in GRADE_TO_GPA:
                await ctx.send(f"❌ Invalid grade: {grade}. Valid grades: A+, A, A-, B+, B, B-, C+, C, C-, D+, D, D-, F")
                return
            gpa_values.append(GRADE_TO_GPA[grade_upper])

        gpa = gpa_calc.calculate_gpa(gpa_values)

        embed = discord.Embed(
            title="📊 GPA Calculation",
            color=discord.Color.green()
        )
        embed.add_field(name="Grades", value=" ".join(grades), inline=False)
        embed.add_field(name="GPA", value=f"**{gpa:.2f}**", inline=False)

        # Add interpretation
        if gpa >= 3.7:
            interpretation = "🌟 Excellent! Dean's List material!"
        elif gpa >= 3.3:
            interpretation = "💪 Great job! Keep it up!"
        elif gpa >= 3.0:
            interpretation = "👍 Good work!"
        elif gpa >= 2.0:
            interpretation = "📈 Room for improvement!"
        else:
            interpretation = "⚠️ Consider seeking academic support"

        embed.add_field(name="Status", value=interpretation, inline=False)

        await ctx.send(embed=embed)

    except Exception as e:
        await ctx.send(f"❌ Error calculating GPA: {str(e)}")


@bot.command(name='calculate_weighted')
async def calculate_weighted(ctx, *course_info):
    """Calculate weighted GPA with credit hours"""
    if not course_info:
        await ctx.send("❌ Please provide grades and credit hours! Example: `!calculate_weighted A,3 B+,4 A-,3`")
        return

    try:
        grades = []
        credits = []

        for course in course_info:
            parts = course.split(',')
            if len(parts) != 2:
                await ctx.send(f"❌ Invalid format: {course}. Use: grade,credits (e.g., A,3)")
                return

            grade, credit = parts[0].upper(), int(parts[1])
            if grade not in GRADE_TO_GPA:
                await ctx.send(f"❌ Invalid grade: {grade}")
                return

            grades.append(GRADE_TO_GPA[grade])
            credits.append(credit)

        gpa = gpa_calc.calculate_gpa(grades, credits)
        total_credits = sum(credits)

        embed = discord.Embed(
            title="📊 Weighted GPA Calculation",
            color=discord.Color.green()
        )

        # Show course breakdown
        course_list = "\n".join([f"{course_info[i].split(',')[0]} ({credits[i]} credits)"
                                 for i in range(len(course_info))])
        embed.add_field(name="Courses", value=course_list, inline=False)
        embed.add_field(name="Total Credits", value=str(total_credits), inline=True)
        embed.add_field(name="Weighted GPA", value=f"**{gpa:.2f}**", inline=True)

        await ctx.send(embed=embed)

    except ValueError:
        await ctx.send("❌ Invalid credit hours. Please use numbers for credits.")
    except Exception as e:
        await ctx.send(f"❌ Error calculating weighted GPA: {str(e)}")


@bot.command(name='add_gpa')
async def add_gpa(ctx, gpa: float, semester: str = None):
    """Add a GPA to your history"""
    if gpa < 0.0 or gpa > 4.0:
        await ctx.send("❌ GPA must be between 0.0 and 4.0")
        return

    user_data.add_gpa(ctx.author.id, gpa, semester)

    embed = discord.Embed(
        title="✅ GPA Added",
        description=f"Added GPA: **{gpa:.2f}**" + (f" for {semester}" if semester else ""),
        color=discord.Color.green()
    )

    await ctx.send(embed=embed)


@bot.command(name='history')
async def history(ctx):
    """View GPA history"""
    user = user_data.get_user(ctx.author.id)

    if not user['gpas']:
        await ctx.send("📚 No GPA history found. Add GPAs using `!add_gpa`")
        return

    embed = discord.Embed(
        title=f"📈 GPA History for {ctx.author.name}",
        color=discord.Color.blue()
    )

    # Create history list
    history_text = ""
    for i, (gpa, semester) in enumerate(zip(user['gpas'], user['semesters'])):
        history_text += f"{semester}: **{gpa:.2f}**\n"

    embed.add_field(name="Semesters", value=history_text, inline=False)

    # Calculate cumulative GPA
    cumulative_gpa = sum(user['gpas']) / len(user['gpas'])
    embed.add_field(name="Cumulative GPA", value=f"**{cumulative_gpa:.2f}**", inline=True)

    # Show trend
    if len(user['gpas']) >= 2:
        trend = "📈 Improving" if user['gpas'][-1] > user['gpas'][-2] else "📉 Declining" if user['gpas'][-1] < \
                                                                                           user['gpas'][
                                                                                               -2] else "➡️ Stable"
        embed.add_field(name="Trend", value=trend, inline=True)

    await ctx.send(embed=embed)


@bot.command(name='predict')
async def predict(ctx):
    """Predict future GPA based on historical data"""
    user = user_data.get_user(ctx.author.id)

    if len(user['gpas']) < 2:
        await ctx.send("📊 Need at least 2 semesters of data to make predictions. Add more GPAs using `!add_gpa`")
        return

    prediction, trend = gpa_calc.predict_gpa(user['gpas'])

    embed = discord.Embed(
        title="🔮 GPA Prediction",
        description=f"Based on your {len(user['gpas'])} semesters of data",
        color=discord.Color.purple()
    )

    # Current stats
    current_gpa = user['gpas'][-1]
    cumulative_gpa = sum(user['gpas']) / len(user['gpas'])

    embed.add_field(name="Current GPA", value=f"{current_gpa:.2f}", inline=True)
    embed.add_field(name="Cumulative GPA", value=f"{cumulative_gpa:.2f}", inline=True)
    embed.add_field(name="Predicted Next GPA", value=f"**{prediction:.2f}**", inline=True)

    # Trend analysis
    if trend > 0.05:
        trend_text = "📈 Strong upward trend! Keep up the great work!"
    elif trend > 0:
        trend_text = "📊 Slight upward trend. You're improving!"
    elif trend < -0.05:
        trend_text = "📉 Downward trend detected. Consider seeking support."
    else:
        trend_text = "➡️ Stable performance."

    embed.add_field(name="Trend Analysis", value=trend_text, inline=False)

    # Recommendations
    if prediction < 2.0:
        rec = "⚠️ **Recommendation**: Meet with an academic advisor immediately."
    elif prediction < 3.0:
        rec = "💡 **Recommendation**: Consider tutoring or study groups."
    elif prediction < 3.5:
        rec = "📚 **Recommendation**: Stay consistent with your study habits."
    else:
        rec = "🌟 **Recommendation**: Excellent trajectory! Consider applying for honors programs."

    embed.add_field(name="Action Items", value=rec, inline=False)

    await ctx.send(embed=embed)


@bot.command(name='stats')
async def stats(ctx):
    """View detailed statistics"""
    user = user_data.get_user(ctx.author.id)

    if not user['gpas']:
        await ctx.send("📊 No data available. Start by adding GPAs using `!add_gpa`")
        return

    gpas = user['gpas']

    embed = discord.Embed(
        title=f"📊 Detailed Statistics for {ctx.author.name}",
        color=discord.Color.gold()
    )

    # Basic stats
    embed.add_field(name="Total Semesters", value=str(len(gpas)), inline=True)
    embed.add_field(name="Cumulative GPA", value=f"{sum(gpas) / len(gpas):.3f}", inline=True)
    embed.add_field(name="Highest GPA", value=f"{max(gpas):.2f}", inline=True)
    embed.add_field(name="Lowest GPA", value=f"{min(gpas):.2f}", inline=True)
    embed.add_field(name="GPA Range", value=f"{max(gpas) - min(gpas):.2f}", inline=True)

    # Standard deviation
    if len(gpas) > 1:
        std_dev = np.std(gpas)
        embed.add_field(name="Consistency (Std Dev)", value=f"{std_dev:.3f}", inline=True)

    # Performance categories
    excellent = sum(1 for g in gpas if g >= 3.7)
    good = sum(1 for g in gpas if 3.0 <= g < 3.7)
    average = sum(1 for g in gpas if 2.0 <= g < 3.0)
    below = sum(1 for g in gpas if g < 2.0)

    performance = f"Excellent (3.7+): {excellent}\n"
    performance += f"Good (3.0-3.69): {good}\n"
    performance += f"Average (2.0-2.99): {average}\n"
    performance += f"Below Average (<2.0): {below}"

    embed.add_field(name="Performance Breakdown", value=performance, inline=False)

    await ctx.send(embed=embed)


@bot.command(name='clear')
async def clear(ctx):
    """Clear your GPA history"""
    user = user_data.get_user(ctx.author.id)
    user['gpas'] = []
    user['semesters'] = []
    user_data.save_data()

    await ctx.send("🗑️ Your GPA history has been cleared.")


# Error handling
@bot.event
async def on_command_error(ctx, error):
    if isinstance(error, commands.CommandNotFound):
        await ctx.send("❌ Command not found. Use `!help_gpa` to see available commands.")
    elif isinstance(error, commands.MissingRequiredArgument):
        await ctx.send(f"❌ Missing required argument: {error.param}")
    else:
        await ctx.send(f"❌ An error occurred: {str(error)}")


# Run the bot
if __name__ == "__main__":
    bot.run(TOKEN)