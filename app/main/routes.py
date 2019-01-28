from datetime import datetime
from flask import render_template, flash, redirect, url_for, request, g, jsonify, current_app
from flask_login import current_user, login_required
from flask_babel import _, get_locale
from guess_language import guess_language
from app import db
from app.main.forms import EditProfileForm, PostForm, SearchForm
from app.models import User, Post
from app.main import bp



import cv2
import numpy as np

from collections import deque

pts = deque()

# Info : ZOOM in the frame to get the RGB value of the corresponding pixel

# The range of color for the object to be detected in HSV
# hsv_supremum = np.array([172, 221, 255])
# hsv_infinum = np.array([150, 40, 130])
hsv_infinum = np.array([100,100,100])
hsv_supremum = np.array([140,255,255])




@bp.before_app_request
def before_request():
    if current_user.is_authenticated:
        current_user.last_seen = datetime.utcnow()
        db.session.commit()
        g.search_form = SearchForm()
    g.locale = str(get_locale())


@bp.route('/', methods=['GET', 'POST'])
@bp.route('/index', methods=['GET', 'POST'])
@login_required
def index():
    form = PostForm()
    if form.validate_on_submit():
        language = guess_language(form.post.data)
        if language == 'UNKNOWN' or len(language) > 5:
            language = ''
        post = Post(body=form.post.data, author=current_user,
                    language=language)
        db.session.add(post)
        db.session.commit()
        flash('Your post is now live!')
        return redirect(url_for('main.index'))
    page = request.args.get('page', 1, type=int)
    posts = current_user.followed_posts().paginate(
        page, current_app.config['POSTS_PER_PAGE'], False)
    next_url = url_for('main.index', page=posts.next_num) if posts.has_next else None
    prev_url = url_for('main.index', page=posts.prev_num) if posts.has_prev else None
    return render_template('index.html', title=_('Home'), form=form, posts=posts.items, next_url=next_url, prev_url=prev_url)


@bp.route('/explore')
@login_required
def explore():
    page = request.args.get('page', 1, type=int)
    posts = Post.query.order_by(Post.timestamp.desc()).paginate(
        page, current_app.config['POSTS_PER_PAGE'], False)
    next_url = url_for('main.explore', page=posts.next_num) if posts.has_next else None
    prev_url = url_for('main.explore', page=posts.prev_num) if posts.has_prev else None
    return render_template('index.html', title=_('Explore'), posts=posts.items, next_url=next_url, prev_url=prev_url)


@bp.route('/user/<username>')
@login_required
def user(username):
    user = User.query.filter_by(username=username).first_or_404()
    page = request.args.get('page', 1, type=int)
    posts = user.posts.order_by(Post.timestamp.desc()).paginate(
        page, current_app.config['POSTS_PER_PAGE'], False)
    next_url = url_for('main.user', username=user.username, page=posts.next_num) if posts.has_next else None
    prev_url = url_for('main.user', username=user.username, page=posts.prev_num) if posts.has_prev else None
    return render_template('user.html', user=user, posts=posts.items, next_url=next_url, prev_url=prev_url)


@bp.route('/edit_profile', methods=['GET', 'POST'])
@login_required
def edit_profile():
    form = EditProfileForm(current_user.username)
    if form.validate_on_submit():
        current_user.username = form.username.data
        current_user.about_me = form.about_me.data
        db.session.commit()
        flash('Your changes have been saved.')
        return redirect(url_for('main.edit_profile'))
    elif request.method == 'GET':
        form.username.data = current_user.username
        form.about_me.data = current_user.about_me
    return render_template('edit_profile.html', title=_('Edit Profile'), form=form)


@bp.route('/follow/<username>')
@login_required
def follow(username):
    user = User.query.filter_by(username=username).first()
    if user is None:
        flash('User %(username)s not found.', username=username)
        return redirect(url_for('main.index'))
    if user == current_user:
        flash('You cannot follow yourself!')
        return redirect(url_for('main.user', username=username))
    current_user.follow(user)
    db.session.commit()
    flash('You are following %(username)s!', username=username)
    return redirect(url_for('main.user', username=username))


@bp.route('/unfollow/<username>')
@login_required
def unfollow(username):
    user = User.query.filter_by(username=username).first()
    if user is None:
        flash('User %(username)s not found.', username=username)
        return redirect(url_for('main.index'))
    if user == current_user:
        flash('You cannot unfollow yourself!')
        return redirect(url_for('main.user', username=username))
    current_user.unfollow(user)
    db.session.commit()
    flash('You are not following %(username)s.', username=username)
    return redirect(url_for('main.user', username=username))



@bp.route('/search')
@login_required
def search():
    if not g.search_form.validate():
        return redirect(url_for('main.explore'))
    page = request.args.get('page', 1, type=int)
    posts, total = Post.search(g.search_form.q.data, page, current_app.config['POSTS_PER_PAGE'])
    next_url = url_for('main.search', q=g.search_form.q.data, page=page + 1) if total > page * current_app.config['POSTS_PER_PAGE'] else None
    prev_url = url_for('main.search', q=g.search_form.q.data, page=page - 1) if page > 1 else None
    return render_template('search.html', title='Search', posts=posts, next_url=next_url, prev_url=prev_url)



@bp.route('/track')
def track():

    cap = cv2.VideoCapture(0)





    while True:
	# Let's capture/read the frames for the video
    	ret, frame = cap.read()

    	if not ret:
    		return("cant open camera")
    		break

    	# This frame captured is flipped, Lets's get the mirror effect
    	frame = cv2.flip(frame, 1)

    	# Any operations on the frame captured will be processed in the operate(frame) method
    	final_frame = operate(frame)

    	# Showing the captured frame
    	cv2.imshow('garrix', frame)
    	cv2.imshow('martin', final_frame)

    	# Continuous, Large amount of frames produce a video
    	# waitkey(value), value is the ammount of millisecs a frame must be displayed
    	# 0xff represents the ASCII value for the key, 27 is for ESC
    	# waitKey is necessary to show a frame
    	if cv2.waitKey(1) & 0xff == 27:
    		break


    cap.release()
    cv2.destroyAllWindows()
    return "tracking blue color"


def operate(frame):
	frame_copy = frame.copy()
	frame_ret = frame.copy()

	# Converting the frame from BGR format to HSV format, Hue Saturation Value GOOGle for more
	frame_copy = cv2.cvtColor(frame, cv2.COLOR_BGR2HSV)

	# Thresholding the frame to get our object(color) tracked
	mask = cv2.inRange(frame_copy, hsv_infinum, hsv_supremum)
	mask = cv2.medianBlur(mask, 5)
	mask = cv2.erode(mask, None, iterations=2)
	mask = cv2.dilate(mask, None, iterations=2)

	#cv2.imshow('mask', mask)

	# Obtaining the binary Image for the corresponding mask
	res = cv2.bitwise_and(frame_ret,frame_ret, mask= mask)

	#cv2.imshow('res', res)
	# The result can be improved by smoothening the frame

	mask_copy = mask.copy()
	cnts = cv2.findContours(mask.copy(), cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_SIMPLE)[-2]
	center = None

	if len(cnts) > 0:
		c = max(cnts, key = cv2.contourArea)
		((x, y), radius) = cv2.minEnclosingCircle(c)

		M = cv2.moments(c)
		center = (int(M["m10"] / M["m00"]), int(M["m01"] / M["m00"]))

		if radius > 10:
			cv2.circle(frame_ret, (int(x), int(y)), int(radius), (0, 150, 255), 2)
			cv2.circle(frame_ret, center, 5, (0, 0, 255), -1)

	pts.appendleft(center)
	#print(pts[0])

	for i in range(1 , len(pts)):
		if pts[i-1] is None or pts[i] is None:
			continue
		thickness = 6
		cv2.line(frame_ret, pts[i-1], pts[i], (0, 0, 255), thickness)


	return frame_ret
