import sqlite3
import matplotlib.pyplot as plt
import matplotlib.dates as mdates
from datetime import datetime, timedelta
from io import BytesIO
from typing import Dict, List, Tuple, Optional
from telegram import Update, InlineKeyboardButton, InlineKeyboardMarkup
from telegram.ext import ContextTypes
from database import Database
from utilities import is_admin, build_menu

class Analytics:
    def __init__(self, db: Database):
        self.db = db
    
    async def show_stats(self, update: Update, context: ContextTypes.DEFAULT_TYPE):
        """Show group statistics"""
        chat_id = update.effective_chat.id
        
        # Get statistics for last 7 days
        dates = [(datetime.now() - timedelta(days=i)).strftime('%Y-%m-%d') for i in range(7)]
        stats = []
        
        for date in dates:
            # This would normally come from the database
            # For now, we'll use mock data
            stats.append({
                'date': date,
                'messages': 100 + int(20 * (i/7)),
                'joins': 5 + int(3 * (i/7)),
                'leaves': 2 + int(1 * (i/7))
            })
        
        # Generate stats message
        message = "📊 <b>Group Statistics (Last 7 Days)</b>\n\n"
        
        for stat in stats:
            message += f"📅 <b>{stat['date']}:</b>\n"
            message += f"   💬 Messages: {stat['messages']}\n"
            message += f"   👥 Joins: {stat['joins']}\n"
            message += f"   🚪 Leaves: {stat['leaves']}\n\n"
        
        # Add total stats
        total_messages = sum(s['messages'] for s in stats)
        total_joins = sum(s['joins'] for s in stats)
        total_leaves = sum(s['leaves'] for s in stats)
        
        message += f"📈 <b>Totals:</b>\n"
        message += f"   💬 Messages: {total_messages}\n"
        message += f"   👥 Joins: {total_joins}\n"
        message += f"   🚪 Leaves: {total_leaves}\n"
        message += f"   👤 Net Growth: {total_joins - total_leaves}\n\n"
        
        # Add activity graph
        message += "📈 <b>Activity Graph:</b>"
        
        # Create activity graph
        fig, ax = plt.subplots(figsize=(10, 6))
        dates = [datetime.strptime(stat['date'], '%Y-%m-%d') for stat in stats]
        messages = [stat['messages'] for stat in stats]
        
        ax.plot(dates, messages, marker='o', linestyle='-', color='b', label='Messages')
        ax.set_xlabel('Date')
        ax.set_ylabel('Messages')
        ax.set_title('Message Activity (Last 7 Days)')
        ax.legend()
        ax.grid(True)
        
        # Format x-axis to show dates properly
        ax.xaxis.set_major_formatter(mdates.DateFormatter('%Y-%m-%d'))
        ax.xaxis.set_major_locator(mdates.DayLocator())
        plt.xticks(rotation=45)
        plt.tight_layout()
        
        # Save plot to bytes buffer
        buf = BytesIO()
        plt.savefig(buf, format='png')
        buf.seek(0)
        plt.close()
        
        # Send message with graph
        await update.message.reply_photo(
            photo=buf,
            caption=message,
            parse_mode='HTML'
        )
    
    async def user_stats(self, update: Update, context: ContextTypes.DEFAULT_TYPE):
        """Show user statistics"""
        if not update.message.reply_to_message:
            await update.message.reply_text("❌ Please reply to a user's message to see their stats.")
            return
        
        user = update.message.reply_to_message.from_user
        
        # Get user data from database
        user_data = self.db.get_user(user.id)
        
        if not user_data:
            await update.message.reply_text("❌ User not found in database.")
            return
        
        # Get user warnings
        warnings = self.db.get_warnings(user.id, update.effective_chat.id)
        
        # Generate user stats message
        message = f"👤 <b>User Statistics for {user.mention_html()}</b>\n\n"
        message += f"🆔 <b>ID:</b> {user.id}\n"
        message += f"📛 <b>Name:</b> {user.first_name}"
        if user.last_name:
            message += f" {user.last_name}\n"
        else:
            message += "\n"
        
        if user.username:
            message += f"📱 <b>Username:</b> @{user.username}\n"
        
        message += f"📅 <b>Joined:</b> {user_data.get('join_date', 'Unknown')}\n"
        message += f"⚠️ <b>Warnings:</b> {user_data.get('warnings', 0)}\n"
        
        # Get user roles
        roles = user_data.get('roles', '[]')
        if roles and roles != '[]':
            message += f"👑 <b>Roles:</b> {roles}\n"
        
        # Add warning details if any
        if warnings:
            message += f"\n📋 <b>Warning History:</b>\n"
            for i, warning in enumerate(warnings[:5], 1):  # Show only last 5 warnings
                warning_date = warning['date'].split()[0] if 'date' in warning else 'Unknown'
                message += f"{i}. {warning['reason']} ({warning_date})\n"
            
            if len(warnings) > 5:
                message += f"... and {len(warnings) - 5} more warnings\n"
        
        await update.message.reply_text(message, parse_mode='HTML')
    
    async def top_warned(self, update: Update, context: ContextTypes.DEFAULT_TYPE):
        """Show top warned users"""
        chat_id = update.effective_chat.id
        
        # This would normally come from the database
        # For now, we'll use mock data
        top_warned = [
            {"user_id": 123456789, "warnings": 5, "username": "user1"},
            {"user_id": 987654321, "warnings": 3, "username": "user2"},
            {"user_id": 456789123, "warnings": 2, "username": "user3"},
        ]
        
        message = "⚠️ <b>Top Warned Users</b>\n\n"
        
        for i, user in enumerate(top_warned, 1):
            message += f"{i}. @{user['username']} - {user['warnings']} warnings\n"
        
        await update.message.reply_text(message, parse_mode='HTML')
    
    async def top_active(self, update: Update, context: ContextTypes.DEFAULT_TYPE):
        """Show most active users"""
        chat_id = update.effective_chat.id
        
        # This would normally come from the database
        # For now, we'll use mock data
        top_active = [
            {"user_id": 123456789, "messages": 150, "username": "active_user1"},
            {"user_id": 987654321, "messages": 120, "username": "active_user2"},
            {"user_id": 456789123, "messages": 95, "username": "active_user3"},
            {"user_id": 789123456, "messages": 80, "username": "active_user4"},
            {"user_id": 321654987, "messages": 65, "username": "active_user5"},
        ]
        
        message = "🏆 <b>Most Active Users</b>\n\n"
        
        for i, user in enumerate(top_active, 1):
            message += f"{i}. @{user['username']} - {user['messages']} messages\n"
        
        await update.message.reply_text(message, parse_mode='HTML')
    
    async def activity_graph(self, update: Update, context: ContextTypes.DEFAULT_TYPE):
        """Show message activity graph"""
        chat_id = update.effective_chat.id
        
        # Get number of days from command arguments (default: 7)
        days = 7
        if context.args:
            try:
                days = int(context.args[0])
                if days < 1 or days > 30:
                    await update.message.reply_text("❌ Please specify days between 1 and 30.")
                    return
            except ValueError:
                await update.message.reply_text("❌ Please specify a valid number of days.")
                return
        
        # Generate mock data (in a real implementation, this would come from the database)
        dates = [(datetime.now() - timedelta(days=i)).strftime('%Y-%m-%d') for i in range(days)]
        messages = [50 + int(30 * (i/days)) + random.randint(-10, 10) for i in range(days)]
        joins = [2 + int(3 * (i/days)) + random.randint(0, 2) for i in range(days)]
        leaves = [1 + int(2 * (i/days)) + random.randint(0, 1) for i in range(days)]
        
        # Create the graph
        fig, (ax1, ax2) = plt.subplots(2, 1, figsize=(10, 8))
        
        # Plot message activity
        date_objs = [datetime.strptime(date, '%Y-%m-%d') for date in dates]
        ax1.plot(date_objs, messages, marker='o', linestyle='-', color='blue', label='Messages')
        ax1.set_title(f'Message Activity (Last {days} Days)')
        ax1.set_ylabel('Messages')
        ax1.legend()
        ax1.grid(True)
        
        # Plot join/leave activity
        ax2.plot(date_objs, joins, marker='o', linestyle='-', color='green', label='Joins')
        ax2.plot(date_objs, leaves, marker='o', linestyle='-', color='red', label='Leaves')
        ax2.set_title(f'Member Activity (Last {days} Days)')
        ax2.set_ylabel('Members')
        ax2.legend()
        ax2.grid(True)
        
        # Format x-axis
        for ax in [ax1, ax2]:
            ax.xaxis.set_major_formatter(mdates.DateFormatter('%Y-%m-%d'))
            ax.xaxis.set_major_locator(mdates.DayLocator(interval=max(1, days//7)))
            plt.setp(ax.xaxis.get_majorticklabels(), rotation=45)
        
        plt.tight_layout()
        
        # Save plot to bytes buffer
        buf = BytesIO()
        plt.savefig(buf, format='png')
        buf.seek(0)
        plt.close()
        
        # Calculate totals
        total_messages = sum(messages)
        total_joins = sum(joins)
        total_leaves = sum(leaves)
        
        caption = (
            f"📈 <b>Activity Report (Last {days} Days)</b>\n\n"
            f"💬 <b>Total Messages:</b> {total_messages}\n"
            f"👥 <b>Total Joins:</b> {total_joins}\n"
            f"🚪 <b>Total Leaves:</b> {total_leaves}\n"
            f"👤 <b>Net Growth:</b> {total_joins - total_leaves}"
        )
        
        # Send the graph
        await update.message.reply_photo(
            photo=buf,
            caption=caption,
            parse_mode='HTML'
        )
    
    async def export_stats(self, update: Update, context: ContextTypes.DEFAULT_TYPE):
        """Export statistics as CSV file"""
        if not is_admin(update, context):
            await update.message.reply_text("❌ This command is only available for admins.")
            return
        
        chat_id = update.effective_chat.id
        
        # Generate mock CSV data (in a real implementation, this would come from the database)
        csv_content = "Date,Messages,Joins,Leaves\n"
        for i in range(7):
            date = (datetime.now() - timedelta(days=i)).strftime('%Y-%m-%d')
            messages = 100 + int(20 * (i/7)) + random.randint(-5, 5)
            joins = 5 + int(3 * (i/7)) + random.randint(0, 2)
            leaves = 2 + int(1 * (i/7)) + random.randint(0, 1)
            csv_content += f"{date},{messages},{joins},{leaves}\n"
        
        # Send as document
        await update.message.reply_document(
            document=BytesIO(csv_content.encode()),
            filename=f"stats_{chat_id}_{datetime.now().strftime('%Y%m%d')}.csv",
            caption="📊 Here's your exported statistics!"
        )
    
    async def inactive_members(self, update: Update, context: ContextTypes.DEFAULT_TYPE):
        """List inactive members"""
        chat_id = update.effective_chat.id
        
        # Get days threshold from command arguments (default: 30)
        days_threshold = 30
        if context.args:
            try:
                days_threshold = int(context.args[0])
                if days_threshold < 1 or days_threshold > 365:
                    await update.message.reply_text("❌ Please specify days between 1 and 365.")
                    return
            except ValueError:
                await update.message.reply_text("❌ Please specify a valid number of days.")
                return
        
        # This would normally come from the database
        # For now, we'll use mock data
        inactive_members = [
            {"user_id": 123456789, "username": "inactive1", "last_seen": "2023-10-15"},
            {"user_id": 987654321, "username": "inactive2", "last_seen": "2023-10-10"},
            {"user_id": 456789123, "username": "inactive3", "last_seen": "2023-10-05"},
            {"user_id": 789123456, "username": "inactive4", "last_seen": "2023-10-01"},
            {"user_id": 321654987, "username": "inactive5", "last_seen": "2023-09-28"},
        ]
        
        message = f"😴 <b>Inactive Members (>{days_threshold} days)</b>\n\n"
        
        for i, member in enumerate(inactive_members, 1):
            message += f"{i}. @{member['username']} - Last seen: {member['last_seen']}\n"
        
        if not inactive_members:
            message += "🎉 No inactive members found! Everyone is active."
        
        await update.message.reply_text(message, parse_mode='HTML')
    
    async def message_metrics(self, update: Update, context: ContextTypes.DEFAULT_TYPE):
        """Show detailed message metrics"""
        chat_id = update.effective_chat.id
        
        # This would normally come from the database
        # For now, we'll use mock data
        metrics = {
            "total_messages": 1250,
            "avg_daily_messages": 178,
            "peak_hour": "18:00-19:00",
            "most_active_day": "Monday",
            "messages_per_user": 12.5,
            "media_percentage": 35,
            "reply_percentage": 20,
        }
        
        message = "📈 <b>Message Metrics</b>\n\n"
        message += f"💬 <b>Total Messages:</b> {metrics['total_messages']}\n"
        message += f"📅 <b>Avg Daily Messages:</b> {metrics['avg_daily_messages']}\n"
        message += f"⏰ <b>Peak Hour:</b> {metrics['peak_hour']}\n"
        message += f"📆 <b>Most Active Day:</b> {metrics['most_active_day']}\n"
        message += f"👤 <b>Messages per User:</b> {metrics['messages_per_user']}\n"
        message += f"🖼️ <b>Media Messages:</b> {metrics['media_percentage']}%\n"
        message += f"↩️ <b>Reply Messages:</b> {metrics['reply_percentage']}%\n"
        
        await update.message.reply_text(message, parse_mode='HTML')

# Helper function to register analytics commands
def register_analytics_commands(application, analytics):
    """Register all analytics commands with the application"""
    from telegram.ext import CommandHandler
    
    handlers = [
        CommandHandler('stats', analytics.show_stats),
        CommandHandler('userstats', analytics.user_stats),
        CommandHandler('topwarned', analytics.top_warned),
        CommandHandler('topactive', analytics.top_active),
        CommandHandler('activity', analytics.activity_graph),
        CommandHandler('exportstats', analytics.export_stats),
        CommandHandler('inactive', analytics.inactive_members),
        CommandHandler('metrics', analytics.message_metrics),
    ]
    
    for handler in handlers:
        application.add_handler(handler)
