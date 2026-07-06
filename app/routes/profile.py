from datetime import datetime
from flask import Blueprint, render_template, request, redirect, url_for, flash
from flask_login import login_required, current_user
from ..extensions import db
from ..models.models import LeetCodeProfile, ContestHistory, Goal
from ..services.leetcode_service import LeetCodeService

profile_bp = Blueprint("profile", __name__, template_folder="../templates")


@profile_bp.route("/", methods=["GET", "POST"])
@login_required
def profile_index():
    lc_profile = current_user.leetcode_profile

    if request.method == "POST":
        leetcode_username = request.form.get("leetcode_username", "").strip()
        if not leetcode_username:
            flash("LeetCode username is required.", "danger")
            return redirect(url_for("profile.profile_index"))

        stats = LeetCodeService.fetch_profile(leetcode_username)
        history = []

        if lc_profile is None:
            lc_profile = LeetCodeProfile(
                user_id=current_user.id, leetcode_username=leetcode_username
            )
            db.session.add(lc_profile)

        lc_profile.leetcode_username = leetcode_username
        lc_profile.total_solved = stats["total_solved"]
        lc_profile.easy_solved = stats["easy_solved"]
        lc_profile.medium_solved = stats["medium_solved"]
        lc_profile.hard_solved = stats["hard_solved"]
        lc_profile.contest_rating = stats["contest_rating"]
        lc_profile.contest_ranking = stats["contest_ranking"]
        lc_profile.acceptance_rate = stats["acceptance_rate"]
        lc_profile.last_synced_at = datetime.utcnow()

        # refresh contest history (for demo, we delete and re-add)
        

        # update goal progress from stats
        goals = Goal.query.filter_by(user_id=current_user.id, status="active").all()
        for g in goals:
            if g.goal_type == "total_solved":
                g.current_value = lc_profile.total_solved
            elif g.goal_type == "easy_solved":
                g.current_value = lc_profile.easy_solved
            elif g.goal_type == "medium_solved":
                g.current_value = lc_profile.medium_solved
            elif g.goal_type == "hard_solved":
                g.current_value = lc_profile.hard_solved
            elif g.goal_type == "contest_rating":
                g.current_value = int(lc_profile.contest_rating or 0)

        db.session.commit()
        flash("LeetCode profile synchronized.", "success")
        return redirect(url_for("profile.profile_index"))

    return render_template("profile.html", lc_profile=lc_profile)
