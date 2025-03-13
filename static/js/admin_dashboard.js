function showEditForm(subjectId) {
    document.getElementById("edit-form-" + subjectId).style.display = "block";
}

function hideEditForm(subjectId) {
    document.getElementById("edit-form-" + subjectId).style.display = "none";
}
function showEditForm_chapter(chapterId) {
    document.getElementById("edit-form-chapter-" + chapterId).style.display = "block";
}

function hideEditForm_chapter(chapterId) {
    document.getElementById("edit-form-chapter-" + chapterId).style.display = "none";
}

function confirmDelete() {
    return confirm("Are you sure you want to delete this chapter?");
}
function showEditForm_quiz(quizId) {
    document.getElementById("edit-form-quiz-" + quizId).style.display = "block";
}

function hideEditForm_quiz(quizId) {
    document.getElementById("edit-form-quiz-" + quizId).style.display = "none";
}

function confirmDeleteQuiz() {
    return confirm("Are you sure you want to delete this quiz?");
}
function showEditForm_question(questionId) {
    document.getElementById("edit-form-question-" + questionId).style.display = "block";
}

function hideEditForm_question(questionId) {
    document.getElementById("edit-form-question-" + questionId).style.display = "none";
}

function confirmDeleteQuestion() {
    return confirm("Are you sure you want to delete this question?");
}