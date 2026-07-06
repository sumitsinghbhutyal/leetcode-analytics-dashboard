from flask import Blueprint, render_template, request
from flask_login import login_required, current_user
from ..extensions import db
from ..models.models import Friend, User, LeetCodeProfile

leaderboard_bp = Blueprint("leaderboard", __name__, template_folder="../templates")


@leaderboard_bp.route("/", methods=["GET", "POST"])
@login_required
def leaderboard_index():
    # Add friend by username or email
    if request.method == "POST":
        identifier = request.form.get("identifier", "").strip()
        friend = User.query.filter(
            (User.username == identifier) | (User.email == identifier)
        ).first()
        if friend and friend.id != current_user.id:
            already = Friend.query.filter_by(
                user_id=current_user.id, friend_user_id=friend.id
            ).first()
            if not already:
                f = Friend(user_id=current_user.id, friend_user_id=friend.id)
                db.session.add(f)
                db.session.commit()
        # Silent if not found; real app should flash message

    sort_by = request.args.get("sort_by", "total_solved")

    friend_links = Friend.query.filter_by(user_id=current_user.id).all()
    friend_ids = [f.friend_user_id for f in friend_links]

    profiles = (
        db.session.query(User, LeetCodeProfile)
        .outerjoin(LeetCodeProfile, User.id == LeetCodeProfile.user_id)
        .filter(User.id.in_(friend_ids))
        .all()
    )

    def sort_key(item):
        user, profile = item
        if not profile:
            return 0
        if sort_by == "contest_rating":
            return profile.contest_rating or 0
        return profile.total_solved or 0

    profiles_sorted = sorted(profiles, key=sort_key, reverse=True)

    return render_template(
        "leaderboard.html", profiles=profiles_sorted, sort_by=sort_by
    )
