from flask import render_template, url_for, flash, redirect, request
from flask_login import login_user, logout_user, login_required, current_user
# Import the app instance along with other objects from your database_models.py
from models.database_models import app, db, bcrypt, login_manager, User, Admin, subject, chapter, quiz, question, score
from flask import Flask

@app.route('/', methods=['GET', 'POST'])
def login_signup():
    if request.method == "POST":
        print("Form is submitted")
        # Get form type from the submitted form data
        form_type = request.form.get("form_type")
        print("Form type:", form_type)
        
        if form_type == "login":
            username = request.form.get("username")
            password = request.form.get("password")
            
            # Check if the user is an admin (using username field)
            admin = Admin.query.filter_by(username=username).first()
            if admin and bcrypt.check_password_hash(admin.password, password):
                login_user(admin)
                return redirect(url_for("admin_dashboard"))
            
            # Check for a regular user (using username field)
            user = User.query.filter_by(username=username).first()
            if user and bcrypt.check_password_hash(user.password, password):
                login_user(user)
                return redirect(url_for("user_dashboard"))
            
            flash("Invalid credentials, if new user please signup", "danger")
        
        elif form_type == "signup":
            username = request.form.get("username")
            email = request.form.get("email")
            password = request.form.get("password")
            
            # Check if a user with this email already exists
            user = User.query.filter_by(email=email).first()
            if user:
                flash("User already exists, please login", "danger")
            else:
                # Hash the password and create a new user
                hashed_password = bcrypt.generate_password_hash(password).decode('utf-8')
                new_user = User(username=username, email=email, password=hashed_password)
                db.session.add(new_user)
                db.session.commit()
                print("User created successfully")
                flash("User created, please login", "success")
                
    return render_template("login.html")

# Admin Dashboard
@app.route("/admin_dashboard", methods=['GET', 'POST'])
@login_required
def admin_dashboard():
    
    if request.method == "POST" or request.method == "GET":
        #For the admin dashboard, we will display the total number of subjects, chapters, quizzes, and questions in the database
        
        #Added this to solve variable umbound error
        chapters_details = []
        questions_details = []
        quizzes_details = []
        user_list = []
        
        total_subjects = subject.query.count()
        total_chapters = chapter.query.count()
        total_quizzes = quiz.query.count()
        total_questions = question.query.count()
        
        #For subject data
        subjects_data = db.session.query(
            subject.id,
            subject.name,
            db.func.count(chapter.id).label("total_chapters")
        ).outerjoin(chapter).group_by(subject.id).all()
        
        # Convert the result to a list of dictionaries
        subjects_list = [{"id": sub.id, "name": sub.name, "chapter_count": sub.total_chapters} for sub in subjects_data]
        
        # Query distinct subject names
        distinct_subjects = db.session.query(subject.name).distinct().all()

        # Convert to a list
        distinct_subject_list = [sub[0] for sub in distinct_subjects]
        
        distinct_chapter = db.session.query(chapter.name).distinct().all()
        distinct_chapter_list = [chap[0] for chap in distinct_chapter]
        
        distinct_quiz = db.session.query(quiz.name).distinct().all()
        distinct_quiz_list = [q[0] for q in distinct_quiz]
        
        user_list = get_user_details()
    #for adding new subject
    if request.method == "POST":
        form_type = request.form.get("form_type")
        if form_type == "add_subject":
            subject_name = request.form.get("subjectname")
            if subject_name is None or subject_name == "":
                flash("Please enter a subject name", "danger")
                return redirect(url_for("admin_dashboard"))
            else:
                check_subject = subject.query.filter_by(name=subject_name).first()
                if check_subject:
                    flash("Subject already exists", "danger")
                    return redirect(url_for("admin_dashboard"))
                else:
                    new_subject = subject(name=subject_name)
                    db.session.add(new_subject)
                    db.session.commit()
                    print("New subject added successfully")
                    flash("New subject added successfully", "success")
                    return redirect(url_for("admin_dashboard"))
                
        elif form_type == "subject_selection_chapter":
            subject_name = request.form.get("selected_subject")
            print("Selected subject:", subject_name)
            print(request.form)
            if subject_name is not None:
                chapters_details = get_chapter_names_for_subject(subject_name)
                print("Chapters details:", chapters_details)
                return render_template("admin_dashboard.html", role="admin", total_subjects=total_subjects, total_chapters=total_chapters, total_quizzes=total_quizzes, total_questions=total_questions, subjects_list=subjects_list, distinct_subject_list=distinct_subject_list, chapters_details=chapters_details, selected_subject=subject_name,distinct_chapter_list=distinct_chapter_list,distinct_quiz_list=distinct_quiz_list,questions_details=questions_details,users_list = user_list)
            else:
                flash("Please select a subject", "danger")
                return redirect(url_for("admin_dashboard"))
            
        elif form_type == "quiz_selection_question":
            selected_quiz = request.form.get("selected_quiz")
            print("Selected quiz:", selected_quiz)
            if selected_quiz is not None:
                questions_details = get_question_details_for_quiz(selected_quiz)
                print("Questions details:", questions_details)
                return render_template("admin_dashboard.html", role="admin", total_subjects=total_subjects, total_chapters=total_chapters, total_quizzes=total_quizzes, total_questions=total_questions, subjects_list=subjects_list, distinct_subject_list=distinct_subject_list, questions_data=questions_details, selected_quiz=selected_quiz,distinct_chapter_list=distinct_chapter_list,distinct_quiz_list=distinct_quiz_list,question_details=questions_details,questions_details=questions_details,users_list = user_list)
            else:
                flash("Please select a quiz", "danger")
                return redirect(url_for("admin_dashboard"))
            
        elif form_type == "add_chapter":
            subject_name = request.form.get("selected_subject")
            chapter_name = request.form.get("chaptername")
            print("Selected subject:", subject_name)
            print("Chapter name:", chapter_name)
            if chapter_name is not None:
                subject_id = subject.query.filter_by(name=subject_name).first().id
                new_chapter = chapter(name=chapter_name, subject_id=subject_id)
                db.session.add(new_chapter)
                db.session.commit()
                print("New chapter added successfully")
                flash("New chapter added successfully", "success")
                return redirect(url_for("admin_dashboard"))
            else:
                flash("Please enter a chapter name", "danger")
                return redirect(url_for("admin_dashboard"))
        
        # New: Select Chapter for Quiz Management
        elif form_type == "chapter_selection_quiz":
            selected_chapter = request.form.get("selected_chapter")
            if selected_chapter:
                quizzes_details = get_quiz_details_for_chapter(selected_chapter)
                return render_template("admin_dashboard.html", role="admin", 
                                       total_subjects=total_subjects, total_chapters=total_chapters, 
                                       total_quizzes=total_quizzes, total_questions=total_questions, 
                                       subjects_list=subjects_list, distinct_subject_list=distinct_subject_list, 
                                       quizzes_details=quizzes_details, selected_chapter=selected_chapter,
                                       distinct_chapter_list=distinct_chapter_list, distinct_quiz_list=distinct_quiz_list,
                                       questions_details=questions_details,users_list = user_list)
            else:
                flash("Please select a chapter", "danger")
                return redirect(url_for("admin_dashboard"))
        
        # New: Add a Quiz for the selected chapter
        elif form_type == "add_quiz":
            selected_chapter = request.form.get("selected_chapter")
            quiz_name = request.form.get("quizname")
            if quiz_name and selected_chapter:
                # Assume chapter is uniquely identified by name (or you might pass an ID instead)
                chapter_obj = chapter.query.filter_by(name=selected_chapter).first()
                if chapter_obj:
                    new_quiz = quiz(name=quiz_name, chapter_id=chapter_obj.id)
                    db.session.add(new_quiz)
                    db.session.commit()
                    flash("New quiz added successfully", "success")
                else:
                    flash("Chapter not found!", "danger")
                return redirect(url_for("admin_dashboard"))
            else:
                flash("Please enter a quiz name and select a chapter", "danger")
                return redirect(url_for("admin_dashboard"))
        
        elif form_type == "add_question":
            selected_quiz = request.form.get("selected_quiz")
            q_text = request.form.get("question")
            opt1 = request.form.get("option1")
            opt2 = request.form.get("option2")
            opt3 = request.form.get("option3")
            opt4 = request.form.get("option4")
            ans = request.form.get("answer")
            
            if selected_quiz and q_text and opt1 and opt2 and opt3 and opt4 and ans:
                # Assuming selected_quiz is the quiz name; ideally, pass quiz_id.
                quiz_obj = quiz.query.filter_by(name=selected_quiz).first()
                if quiz_obj:
                    new_question = question(question=q_text, option1=opt1, option2=opt2,
                                            option3=opt3, option4=opt4, answer=ans, quiz_id=quiz_obj.id)
                    db.session.add(new_question)
                    db.session.commit()
                    flash("New question added successfully", "success")
                else:
                    flash("Quiz not found", "danger")
            else:
                flash("Please fill in all fields", "danger")
            return redirect(url_for("admin_dashboard"))
        
        elif form_type == "add_question":
            selected_quiz = request.form.get("selected_quiz")
            q_text = request.form.get("question")
            opt1 = request.form.get("option1")
            opt2 = request.form.get("option2")
            opt3 = request.form.get("option3")
            opt4 = request.form.get("option4")
            ans = request.form.get("answer")
            
            if selected_quiz and q_text and opt1 and opt2 and opt3 and opt4 and ans:
                # Assuming selected_quiz is the quiz name; ideally, pass quiz_id.
                quiz_obj = quiz.query.filter_by(name=selected_quiz).first()
                if quiz_obj:
                    new_question = question(question=q_text, option1=opt1, option2=opt2,
                                            option3=opt3, option4=opt4, answer=ans, quiz_id=quiz_obj.id)
                    db.session.add(new_question)
                    db.session.commit()
                    flash("New question added successfully", "success")
                else:
                    flash("Quiz not found", "danger")
            else:
                flash("Please fill in all fields", "danger")
            return redirect(url_for("admin_dashboard"))

        
    return render_template("admin_dashboard.html", role="admin", 
                           total_subjects=total_subjects, total_chapters=total_chapters, 
                           total_quizzes=total_quizzes, total_questions=total_questions, 
                           subjects_list=subjects_list, distinct_subject_list=distinct_subject_list,
                           distinct_chapter_list=distinct_chapter_list, distinct_quiz_list=distinct_quiz_list,
                           questions_details=questions_details,users_list = user_list)

@app.route('/edit', methods=['POST'])
def edit():
    if request.form.get('form_type') == 'subject_edit':
        subject_id = request.form.get('subject_id')
        new_name = request.form.get('new_name')

        if subject_id and new_name:
            # Find the subject in the database
            sub = subject.query.get(subject_id)
            if sub:
                sub.name = new_name
                db.session.commit()
                flash("Subject updated successfully!", "success")
            else:
                flash("Subject not found!", "danger")
        else:
            flash("Invalid data provided!", "danger")

        return redirect(url_for('admin_dashboard'))  # Always return a response
    
    elif request.form.get('form_type') == 'chapter_edit':
        chapter_id = request.form.get('chapter_id')
        new_name = request.form.get('new_name')

        if chapter_id and new_name:
            # Find the chapter in the database
            chap = chapter.query.get(chapter_id)
            if chap:
                chap.name = new_name
                db.session.commit()
                flash("Chapter updated successfully!", "success")
            else:
                flash("Chapter not found!", "danger")
        else:
            flash("Invalid data provided!", "danger")

        return redirect(url_for('admin_dashboard'))
    
    elif request.form.get('form_type') == 'quiz_edit':
        quiz_id = request.form.get('quiz_id')
        new_name = request.form.get('new_name')
        if quiz_id and new_name:
            quiz_obj = quiz.query.get(quiz_id)
            if quiz_obj:
                quiz_obj.name = new_name
                db.session.commit()
                flash("Quiz updated successfully!", "success")
            else:
                flash("Quiz not found!", "danger")
        else:
            flash("Invalid data provided!", "danger")
    
    elif request.form.get('form_type') == 'question_edit':
        question_id = request.form.get('question_id')
        new_question = request.form.get('new_question')
        new_option1 = request.form.get('new_option1')
        new_option2 = request.form.get('new_option2')
        new_option3 = request.form.get('new_option3')
        new_option4 = request.form.get('new_option4')
        new_answer = request.form.get('new_answer')

        if question_id and new_question and new_option1 and new_option2 and new_option3 and new_option4 and new_answer:
            # Find the question in the database
            ques = question.query.get(question_id)
            if ques:
                ques.question = new_question
                ques.option1 = new_option1
                ques.option2 = new_option2
                ques.option3 = new_option3
                ques.option4 = new_option4
                ques.answer = new_answer
                db.session.commit()
                flash("Question updated successfully!", "success")
            else:
                flash("Question not found!", "danger")
        else:
            flash("Invalid data provided!", "danger")

        return redirect(url_for('admin_dashboard'))   
    
        
    # If form_type is not subject_edit, return an error
    flash("Invalid request!", "danger")
    return redirect(url_for('admin_dashboard'))  # Ensure a valid response

@app.route('/delete', methods=['POST'])
def delete():
    if request.form.get('form_type') == 'subject_delete':
        subject_id = request.form.get('subject_id')

        if subject_id:
            # Find the subject in the database
            sub = subject.query.get(subject_id)
            if sub:
                # Loop through each chapter in this subject
                for chap in sub.chapters:
                    # Loop through each quiz in this chapter
                    for q in chap.quizzes:
                        # Optionally, delete related scores first if needed
                        for score_obj in q.scores:
                            db.session.delete(score_obj)
                        # Delete all questions in the quiz
                        for ques in q.questions:
                            db.session.delete(ques)
                        # Delete the quiz itself
                        db.session.delete(q)
                    # Delete the chapter
                    db.session.delete(chap)
                # Finally, delete the subject
                db.session.delete(sub)
                db.session.commit()
                flash("Subject and all associated chapters, quizzes, and questions deleted successfully!", "success")
            else:
                flash("Subject not found!", "danger")
        else:
            flash("Invalid data provided!", "danger")

        return redirect(url_for('admin_dashboard'))

    
    elif request.form.get("form_type") == "chapter_delete":
        chapter_id = request.form.get("chapter_id")

        if chapter_id:
            chapter_obj = chapter.query.get(chapter_id)
            if chapter_obj:
                db.session.delete(chapter_obj)
                db.session.commit()
                flash("Chapter deleted successfully!", "success")
            else:
                flash("Chapter not found!", "danger")

    elif request.form.get('form_type') == 'quiz_delete':
        quiz_id = request.form.get('quiz_id')
        if quiz_id:
            quiz_obj = quiz.query.get(quiz_id)
            if quiz_obj:
                # Delete related scores if needed
                for score_obj in quiz_obj.scores:
                    db.session.delete(score_obj)
                # Delete all related questions
                for ques in quiz_obj.questions:
                    db.session.delete(ques)
                db.session.delete(quiz_obj)
                db.session.commit()
                flash("Quiz deleted successfully!", "success")
            else:
                flash("Quiz not found!", "danger")
        else:
            flash("Invalid data provided!", "danger")
            
    elif request.form.get('form_type') == 'question_delete':
        question_id = request.form.get('question_id')
        if question_id:
            question_obj = question.query.get(question_id)
            if question_obj:
                db.session.delete(question_obj)
                db.session.commit()
                flash("Question deleted successfully!", "success")
            else:
                flash("Question not found!", "danger")
        else:
            flash("Invalid data provided!", "danger")
    
    # If form_type is not subject_delete, return an error
    flash("Invalid request!", "danger")
    return redirect(url_for('admin_dashboard'))  # Ensure a valid response

# User Dashboard
@app.route("/user_dashboard")
@login_required
def user_dashboard():
    # Query all subjects; each subject automatically loads its chapters,
    # and each chapter loads its quizzes (if lazy loading is enabled).
    all_subjects = subject.query.all()
    print("All subjects:", all_subjects)
    return render_template("user_dashboard.html", role="user", subjects=all_subjects)

@app.route('/take_quiz/<int:quiz_id>', methods=['GET', 'POST'])
@login_required
def take_quiz(quiz_id):
    # Get the quiz object; 404 if not found.
    quiz_obj = quiz.query.get_or_404(quiz_id)
    print("Quiz object:", quiz_obj)
    # Retrieve all questions for the quiz.
    questions = question.query.filter_by(quiz_id=quiz_id).all()
    
    # Set a time limit. For example, if your quiz model has a time_duration field,
    # you can use that; otherwise, use a default (e.g., 60 seconds per question).
    time_limit = getattr(quiz_obj, 'time_duration', 60 * len(questions))
    
    if request.method == 'POST':
        # Evaluate the submitted answers.
        score_val = 0
        feedback = []
        for ques in questions:
            # Get the submitted answer for question id 'q_{id}'
            selected_answer = request.form.get(f"q_{ques.id}")
            is_correct = (selected_answer == ques.answer)
            if is_correct:
                score_val += 1
            feedback.append({
                "question": ques.question,
                "selected": selected_answer,
                "correct": ques.answer,
                "result": "Correct" if is_correct else "Incorrect"
            })
            print("Marked for question:", ques.id, "is correct?", is_correct)
        print("Final score:", score_val)
        
        # Store the quiz score in the database.
        new_score = score(score=score_val, user_id=current_user.id, quiz_id=quiz_id)
        db.session.add(new_score)
        db.session.commit()
        
        # Render a feedback page with details.
        return render_template("quiz_feedback.html", quiz=quiz_obj, score=score_val, total=len(questions), feedback=feedback)
    
    # GET: Render the quiz attempt page with the questions and time limit.
    return render_template("take_quiz.html", quiz=quiz_obj, questions=questions, time_limit=time_limit)


# Logout Route
@app.route("/logout")
@login_required
def logout():
    logout_user()
    return redirect(url_for("login_signup"))

def get_chapter_names_for_subject(subject_name):
    chapters_data = db.session.query(
        chapter.id,
        chapter.name,
        db.func.count(quiz.id).label("total_quizzes")
    ).join(subject).outerjoin(quiz) \
    .filter(subject.name == subject_name) \
    .group_by(chapter.id).all()
    
    return [{"id": ch.id, "name": ch.name, "total_quizzes": ch.total_quizzes} for ch in chapters_data]

def get_quiz_details_for_chapter(chapter_name):
    # Find the chapter by its name
    chap = chapter.query.filter_by(name=chapter_name).first()
    if chap:
        quizzes_data = db.session.query(
            quiz.id,
            quiz.name,
            db.func.count(question.id).label("total_questions")
        ).outerjoin(question).filter(quiz.chapter_id == chap.id).group_by(quiz.id).all()
        return [{"id": q.id, "name": q.name, "total_questions": q.total_questions} for q in quizzes_data]
    else:
        return []
    
def get_question_details_for_quiz(quiz_name):
    # Find the quiz by its name
    qz = quiz.query.filter_by(name=quiz_name).first()
    if qz:
        questions_data = db.session.query(
            question.id,
            question.question,
            question.option1,
            question.option2,
            question.option3,
            question.option4,
            question.answer
        ).filter(question.quiz_id == qz.id).all()
        return [{"id": q.id, "question": q.question, "option1": q.option1, "option2": q.option2, "option3": q.option3, "option4": q.option4, "answer": q.answer} for q in questions_data]
    else:
        return []

def get_user_details():
    #Find user details for all users
    user_data = db.session.query(
        User.id,
        User.username,
        User.email
    ).all()
    return [{"id": u.id, "username": u.username, "email": u.email} for u in user_data]
    

if __name__ == "__main__":
    app.run(debug=True)