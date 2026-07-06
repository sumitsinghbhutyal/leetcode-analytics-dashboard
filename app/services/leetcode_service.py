import json
from collections import defaultdict
from datetime import datetime

import requests


class LeetCodeService:
    """
    Service layer responsible for communicating with LeetCode's
    GraphQL API and converting responses into a format that the
    rest of the Flask application understands.
    """

    GRAPHQL_URL = "https://leetcode.com/graphql"

    HEADERS = {
        "Content-Type": "application/json",
        "Referer": "https://leetcode.com",
        "Origin": "https://leetcode.com",
        "User-Agent": (
            "Mozilla/5.0 (Windows NT 10.0; Win64; x64) "
            "AppleWebKit/537.36 (KHTML, like Gecko) "
            "Chrome/126.0 Safari/537.36"
        ),
    }

    PROFILE_QUERY = """
    query getProfile($username: String!) {

      matchedUser(username: $username) {

        username

        profile {
          realName
          userAvatar
          ranking
          reputation
          starRating
          aboutMe
        }

        submitStatsGlobal {
          acSubmissionNum {
            difficulty
            count
            submissions
          }
        }

        userCalendar {
          submissionCalendar
        }

      }

      userContestRanking(username: $username) {

        rating
        globalRanking
        attendedContestsCount
        topPercentage

      }

    }
    """

    RECENT_SUBMISSIONS_QUERY = """
    query recentSubmissions($username: String!) {

      recentSubmissionList(username: $username) {

        title
        titleSlug
        statusDisplay
        lang
        timestamp

      }

    }
    """

    @staticmethod
    def _make_request(query, variables):
        """
        Generic GraphQL request helper.
        """

        response = requests.post(
            LeetCodeService.GRAPHQL_URL,
            json={
                "query": query,
                "variables": variables,
            },
            headers=LeetCodeService.HEADERS,
            timeout=20,
        )

        response.raise_for_status()

        payload = response.json()

        if "errors" in payload:
            raise Exception(payload["errors"][0]["message"])

        return payload["data"]

    @staticmethod
    def _parse_calendar(calendar_string):
        """
        Converts LeetCode's submission calendar JSON string
        into a Python dictionary.
        """

        if not calendar_string:
            return {}

        try:
            return json.loads(calendar_string)
        except Exception:
            return {}

    @staticmethod
    def _calculate_acceptance_rate(stats):

        accepted = 0
        submissions = 0

        for item in stats:

            if item["difficulty"] == "All":

                accepted = item.get("count", 0)
                submissions = item.get("submissions", accepted)

                break

        if submissions == 0:
            return 0.0

        return round((accepted / submissions) * 100, 2)

    @staticmethod
    def fetch_profile(username):

        data = LeetCodeService._make_request(
            LeetCodeService.PROFILE_QUERY,
            {
                "username": username
            },
        )

        user = data.get("matchedUser")

        if user is None:
            raise Exception("LeetCode user not found.")

        profile = user.get("profile", {})
        contest = data.get("userContestRanking") or {}

        stats = (
            user.get("submitStatsGlobal", {})
            .get("acSubmissionNum", [])
        )

        total = 0
        easy = 0
        medium = 0
        hard = 0

        for item in stats:

            difficulty = item.get("difficulty")

            if difficulty == "All":
                total = item.get("count", 0)

            elif difficulty == "Easy":
                easy = item.get("count", 0)

            elif difficulty == "Medium":
                medium = item.get("count", 0)

            elif difficulty == "Hard":
                hard = item.get("count", 0)

        acceptance_rate = (
            LeetCodeService._calculate_acceptance_rate(stats)
        )

        calendar = LeetCodeService._parse_calendar(
            user.get("userCalendar", {})
            .get("submissionCalendar", "{}")
        )

        return {

            # Existing fields used by your Flask routes

            "total_solved": total,

            "easy_solved": easy,

            "medium_solved": medium,

            "hard_solved": hard,

            "contest_rating": contest.get("rating", 0),

            "contest_ranking": contest.get("globalRanking", 0),

            "acceptance_rate": acceptance_rate,

            # Extra fields for future dashboard improvements

            "username": user.get("username"),

            "real_name": profile.get("realName"),

            "avatar": profile.get("userAvatar"),

            "ranking": profile.get("ranking"),

            "reputation": profile.get("reputation"),

            "star_rating": profile.get("starRating"),

            "about": profile.get("aboutMe"),

            "contest_count": contest.get(
                "attendedContestsCount",
                0,
            ),

            "top_percentage": contest.get(
                "topPercentage",
                0,
            ),

            "calendar": calendar,

        }
    @staticmethod
    def fetch_recent_submissions(username, limit=10):
        """
        Returns the user's most recent submissions.
        """

        data = LeetCodeService._make_request(
            LeetCodeService.RECENT_SUBMISSIONS_QUERY,
            {
                "username": username
            },
        )

        submissions = data.get("recentSubmissionList", [])

        result = []

        for submission in submissions[:limit]:

            try:
                timestamp = datetime.fromtimestamp(
                    int(submission["timestamp"])
                ).strftime("%d %b %Y %H:%M")

            except Exception:
                timestamp = submission.get("timestamp")

            result.append(
                {
                    "title": submission.get("title"),
                    "title_slug": submission.get("titleSlug"),
                    "status": submission.get("statusDisplay"),
                    "language": submission.get("lang"),
                    "timestamp": timestamp,
                }
            )

        return result

    @staticmethod
    def _calendar_to_monthly_activity(calendar):

        monthly = defaultdict(int)

        for unix_time, submissions in calendar.items():

            try:

                dt = datetime.fromtimestamp(int(unix_time))

                month = dt.strftime("%Y-%m")

                monthly[month] += submissions

            except Exception:
                continue

        return dict(sorted(monthly.items()))

    @staticmethod
    def _calendar_to_daily_activity(calendar):

        daily = {}

        for unix_time, submissions in calendar.items():

            try:

                dt = datetime.fromtimestamp(
                    int(unix_time)
                ).strftime("%Y-%m-%d")

                daily[dt] = submissions

            except Exception:
                continue

        return dict(sorted(daily.items()))

    @staticmethod
    def _calculate_current_streak(calendar):

        if not calendar:
            return 0

        days = sorted(
            [
                datetime.fromtimestamp(int(ts)).date()
                for ts in calendar.keys()
            ]
        )

        if not days:
            return 0

        streak = 0
        today = datetime.now().date()

        current = today

        day_set = set(days)

        while current in day_set:

            streak += 1

            current = current.fromordinal(
                current.toordinal() - 1
            )

        return streak

    @staticmethod
    def _calculate_longest_streak(calendar):

        if not calendar:
            return 0

        days = sorted(
            [
                datetime.fromtimestamp(int(ts)).date()
                for ts in calendar.keys()
            ]
        )

        if not days:
            return 0

        longest = 1
        current = 1

        for i in range(1, len(days)):

            if (
                days[i].toordinal()
                == days[i - 1].toordinal() + 1
            ):
                current += 1
                longest = max(longest, current)

            else:
                current = 1

        return longest

    @staticmethod
    def fetch_monthly_activity(username):

        profile = LeetCodeService.fetch_profile(username)

        calendar = profile.get("calendar", {})

        return LeetCodeService._calendar_to_monthly_activity(
            calendar
        )

    @staticmethod
    def fetch_activity_summary(username):

        profile = LeetCodeService.fetch_profile(username)

        calendar = profile.get("calendar", {})

        return {
            "monthly_activity":
                LeetCodeService._calendar_to_monthly_activity(
                    calendar
                ),

            "daily_activity":
                LeetCodeService._calendar_to_daily_activity(
                    calendar
                ),

            "current_streak":
                LeetCodeService._calculate_current_streak(
                    calendar
                ),

            "longest_streak":
                LeetCodeService._calculate_longest_streak(
                    calendar
                ),

            "total_active_days":
                len(calendar),
        }
    @staticmethod
    def fetch_contest_history(username):
        """
        Placeholder.

        LeetCode's currently verified GraphQL queries do not expose
        historical contest ratings.

        Returning an empty list keeps the existing Flask routes
        working without generating fake data.
        """
        return []

    @staticmethod
    def get_profile_summary(username):
        """
        Returns a richer profile object for future dashboard upgrades.
        """

        profile = LeetCodeService.fetch_profile(username)

        activity = LeetCodeService.fetch_activity_summary(username)

        recent = LeetCodeService.fetch_recent_submissions(
            username,
            limit=5,
        )

        return {

            "profile": profile,

            "activity": activity,

            "recent_submissions": recent,

        }

    @staticmethod
    def sync_profile(username):
        """
        Convenience wrapper.

        Used if later background jobs or scheduled syncs are added.
        """

        return LeetCodeService.fetch_profile(username)

    @staticmethod
    def health_check():
        """
        Checks whether LeetCode GraphQL is reachable.
        """

        try:

            LeetCodeService._make_request(
                """
                query {
                    __typename
                }
                """,
                {},
            )

            return True

        except Exception:

            return False
        