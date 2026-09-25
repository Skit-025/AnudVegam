"""
Dialogue Service - Interview Coordinator Service
=================================================

File Purpose:
-------------
Central orchestrator within the Dialogue AI microservice.
Evaluates the patient's incoming Q&A history, assesses clinical red flags,
and drives the dynamic question tree.
"""

from ..schemas.dialogue import NextQuestionRequest, NextQuestionResponse, RedFlagAlert
from ..rules.question_tree import QuestionTreeEngine
from ..rules.red_flags import RedFlagRuleEngine


class InterviewService:
    """
    Coordinates question navigation and real-time clinical red-flag detection.
    """

    def __init__(self):
        self.question_engine = QuestionTreeEngine()
        self.red_flag_engine = RedFlagRuleEngine()

    def process_next_step(self, request: NextQuestionRequest) -> NextQuestionResponse:
        """
        Coordinate the next interview step for a given patient intake session.
        """
        # Step 1: Evaluate latest response for immediate red-flag indicators
        latest_alert = RedFlagAlert(detected=False, severity="INFO", reason=None)
        if request.previous_answers:
            last_ans = request.previous_answers[-1]
            latest_alert = self.red_flag_engine.evaluate_response(
                last_ans.question_key,
                last_ans.answer_text
            )

        # Step 2: Evaluate composite risk across the entire session history
        cumulative_alert = self.red_flag_engine.evaluate_cumulative_history(request.previous_answers)

        # Merge alerts prioritizing CRITICAL > URGENT > INFO
        if latest_alert.detected and latest_alert.severity == "CRITICAL":
            active_alert = latest_alert
        elif cumulative_alert.detected and cumulative_alert.severity == "CRITICAL":
            active_alert = cumulative_alert
        elif latest_alert.detected:
            active_alert = latest_alert
        elif cumulative_alert.detected:
            active_alert = cumulative_alert
        else:
            active_alert = RedFlagAlert(detected=False, severity="INFO", reason=None)

        # Step 3: Compute the next question node via the dynamic question tree engine
        next_q = self.question_engine.get_next_question(
            mode=request.mode,
            previous_answers=request.previous_answers,
            language=request.language
        )

        # Step 4: Attach the active red flag assessment to the response
        next_q.red_flag = active_alert

        return next_q
