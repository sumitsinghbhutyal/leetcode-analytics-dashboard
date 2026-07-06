from flask import Blueprint, jsonify
from flask_login import login_required, current_user
from ..models.models import LeetCodeProfile, ContestHistory
from ..services.leetcode_service import LeetCodeService

api_bp = Blueprint("api", __name__)


@api_bp.route("/stats")
@login_required
def api_stats():
    lc_profile = current_user.leetcode_profile
    if not lc_profile:
        return jsonify({"error": "No profile"}), 404

    data = {
        "total_solved": lc_profile.total_solved,
        "easy_solved": lc_profile.easy_solved,
        "medium_solved": lc_profile.medium_solved,
        "hard_solved": lc_profile.hard_solved,
        "contest_rating": lc_profile.contest_rating,
        "contest_ranking": lc_profile.contest_ranking,
        "acceptance_rate": lc_profile.acceptance_rate,
    }
    return jsonify(data)


@api_bp.route("/difficulty-distribution")
@login_required
def difficulty_distribution():
    lc_profile = current_user.leetcode_profile
    if not lc_profile:
        return jsonify({"error": "No profile"}), 404
    data = {
        "labels": ["Easy", "Medium", "Hard"],
        "values": [
            lc_profile.easy_solved,
            lc_profile.medium_solved,
            lc_profile.hard_solved,
        ],
    }
    return jsonify(data)


@api_bp.route("/contest-history")
@login_required
def contest_history():
    contests = (
        ContestHistory.query.filter_by(user_id=current_user.id)
        .order_by(ContestHistory.contest_date.asc())
        .all()
    )
    data = {
        "labels": [c.contest_name for c in contests],
        "ratings": [c.rating for c in contests],
        "dates": [c.contest_date.isoformat() for c in contests],
    }
    return jsonify(data)


@api_bp.route("/activity")
@login_required
def activity():
    lc_profile = current_user.leetcode_profile
    if not lc_profile:
        return jsonify({"labels": [], "values": []})

    monthly_activity = LeetCodeService.fetch_monthly_activity(
        lc_profile.leetcode_username
    )
    labels = sorted(monthly_activity.keys())
    values = [monthly_activity[m] for m in labels]
    return jsonify({"labels": labels, "values": values})
