from flask import Blueprint, render_template, url_for, redirect, request, flash
from flask_login import current_user

from .. import client
from ..forms import MusicReviewForm, SearchForm
from ..models import User, Review
from ..utils import current_time

music = Blueprint("music", __name__)

@music.route('/', methods=['GET', 'POST'])
def index():
    form = SearchForm()

    if form.validate_on_submit():
        return redirect(url_for('music.query_results', query=form.search_query.data, input_type=form.input_type.data))

    return render_template('index.html', form=form)

@music.route('/search-results/<query>?<input_type>', methods=['GET'])
def query_results(query, input_type):
    try:
        results = client.get_search_results(query=query, search_type=input_type)
        return render_template('query_results.html', results=results, input_type=input_type)
    except ValueError as err:
        return render_template('query_results.html', error_msg=err)


@music.route("/music/<music_id>", methods=["GET", "POST"])
def music_detail(music_id):
    try:
        result = client.get_track(id)
    except ValueError as e:
        flash(str(e))
        return redirect(url_for("users.login"))

    form = MusicReviewForm()
    if form.validate_on_submit() and current_user.is_authenticated:
        review = Review(
            commenter=current_user._get_current_object(),
            content=form.text.data,
            date=current_time(),
            track_id=music_id,
            song_title=result.title,
        )
        review.save()

        return redirect(request.path)

    reviews = Review.objects(track_id=id)

    return render_template(
        "song_detail.html", form=form, song=result, reviews=reviews
    )


@music.route("/user/<username>")
def user_detail(username):
    user = User.objects(username=username).first()
    reviews = Review.objects(commenter=user)

    return render_template("user_detail.html", username=username, reviews=reviews)
