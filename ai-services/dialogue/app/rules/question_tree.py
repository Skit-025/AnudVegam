"""
Dialogue Service - Dynamic Medical Question Tree Engine
========================================================

File Purpose:
-------------
Executes dynamic rule-based branching decision-tree logic for clinical intake questions
across both Allopathic and AYUSH (Ayurveda, Yoga, Unani, Siddha, Homeopathy) OPD pathways.

What it does:
-------------
1. Dynamically selects the next question by analyzing patient's chief complaint, duration, and responses.
2. Supports multilingual prompts (English, Hindi, Marathi).
3. Automatically marks final question (`is_final = True`) once comprehensive clinical intake is captured.
"""

import re
from typing import Dict, Any, List, Optional
from ..schemas.dialogue import ClinicalMode, InputType, PreviousAnswer, NextQuestionResponse


class QuestionNode:
    def __init__(
        self,
        key: str,
        prompts: Dict[str, str],
        input_type: InputType,
        options: Optional[List[str]] = None,
        next_default: Optional[str] = None,
        branches: Optional[Dict[str, str]] = None,
        is_final: bool = False
    ):
        self.key = key
        self.prompts = prompts
        self.input_type = input_type
        self.options = options or []
        self.next_default = next_default
        self.branches = branches or {}
        self.is_final = is_final

    def get_prompt(self, language: str) -> str:
        return self.prompts.get(language) or self.prompts.get("en") or next(iter(self.prompts.values()))


class QuestionTreeEngine:
    """
    Core dynamic rule-based question tree router for Allopathic and AYUSH workflows.
    """

    def __init__(self):
        self.allopathic_nodes: Dict[str, QuestionNode] = self._build_allopathic_tree()
        self.ayush_nodes: Dict[str, QuestionNode] = self._build_ayush_tree()

    def _build_allopathic_tree(self) -> Dict[str, QuestionNode]:
        nodes = {}

        # 1. Chief Complaint
        nodes["chief_complaint"] = QuestionNode(
            key="chief_complaint",
            prompts={
                "en": "What is your main health concern or reason for visiting the OPD today?",
                "hi": "आज ओपीडी में आने का आपका मुख्य कारण या मुख्य लक्षण क्या है?",
                "mr": "आज ओपीडीमध्ये येण्याचे तुमचे मुख्य कारण किंवा लक्षण काय आहे?"
            },
            input_type=InputType.FREE_TEXT_OR_VOICE,
            options=["Fever / Chills", "Chest Pain / Discomfort", "Cough / Breathlessness", "Abdominal / Stomach Pain", "Joint Pain / Body Ache", "Headache / Dizziness", "Other Concern"],
            next_default="symptom_duration"
        )

        # 2. Category Branch: Fever pathway
        nodes["fever_duration"] = QuestionNode(
            key="fever_duration",
            prompts={
                "en": "How many days have you had this fever, and what was the highest temperature measured?",
                "hi": "आपको यह बुखार कितने दिनों से है और अधिकतम तापमान कितना रहा है?",
                "mr": "हा ताप तुम्हाला किती दिवसांपासून आहे आणि कमाल तापमान किती होते?"
            },
            input_type=InputType.SINGLE_CHOICE,
            options=["Less than 2 days", "3 to 5 days", "1 to 2 weeks", "More than 2 weeks"],
            next_default="fever_associated"
        )
        nodes["fever_associated"] = QuestionNode(
            key="fever_associated",
            prompts={
                "en": "Do you have any chills, body aches, shivering, skin rash, or vomiting with the fever?",
                "hi": "क्या बुखार के साथ ठंड लगना, कंपकंपी, शरीर में दर्द, दाने या उल्टी है?",
                "mr": "तापाबरोबर थंडी वाजणे, थरथरणे, अंगदुखी, पुरळ किंवा उलट्या आहेत का?"
            },
            input_type=InputType.MULTI_CHOICE,
            options=["Chills and shivering", "Skin rash or spots", "Nausea or vomiting", "Severe headache", "None of these"],
            next_default="past_medical_history"
        )

        # 3. Category Branch: Chest Pain pathway
        nodes["chest_pain_character"] = QuestionNode(
            key="chest_pain_character",
            prompts={
                "en": "Describe the chest discomfort: Is it crushing heaviness, sharp pricking, burning, or aching?",
                "hi": "छाती के दर्द का विवरण दें: क्या यह भारी दबाव, चुभन, जलन या हल्का दर्द है?",
                "mr": "छातीतील वेदनेचे वर्णन करा: खूप जड वाटणे, टोचणे, जळजळ किंवा ठणकणे आहे का?"
            },
            input_type=InputType.SINGLE_CHOICE,
            options=["Crushing pressure / Heaviness", "Burning sensation", "Sharp stabbing pain", "Dull ache"],
            next_default="chest_pain_radiation"
        )
        nodes["chest_pain_radiation"] = QuestionNode(
            key="chest_pain_radiation",
            prompts={
                "en": "Does the pain spread or radiate to your left arm, shoulder, jaw, neck, or upper back?",
                "hi": "क्या यह दर्द आपके बाएं हाथ, कंधे, जबड़े, गर्दन या पीठ में फैलता है?",
                "mr": "हा त्रास तुमच्या डाव्या हाताला, खांद्याला, जबड्याला, मानेला किंवा पाठीला जाणवतो का?"
            },
            input_type=InputType.SINGLE_CHOICE,
            options=["Yes, radiating to left arm/jaw", "Yes, radiating to back", "No radiation, localized to center", "No radiation, localized to ribs"],
            next_default="past_medical_history"
        )

        # 4. Category Branch: Cough / Respiratory pathway
        nodes["cough_details"] = QuestionNode(
            key="cough_details",
            prompts={
                "en": "Is your cough dry or producing phlegm/mucus? Have you noticed any blood in the sputum?",
                "hi": "क्या आपकी खांसी सूखी है या बलगम वाली? क्या बलगम में खून दिखाई दिया है?",
                "mr": "तुमचा खोकला कोरडा आहे की कफयुक्त? कफामध्ये रक्त दिसले आहे का?"
            },
            input_type=InputType.SINGLE_CHOICE,
            options=["Dry irritating cough", "Wet cough with yellow/green phlegm", "Blood in sputum (Hemoptysis)", "Cough with wheezing / whistling sound"],
            next_default="breathing_difficulty"
        )
        nodes["breathing_difficulty"] = QuestionNode(
            key="breathing_difficulty",
            prompts={
                "en": "Are you experiencing difficulty breathing while resting or only while walking/exerting?",
                "hi": "क्या आपको सांस लेने में तकलीफ आराम करते समय भी होती है या केवल चलने पर?",
                "mr": "श्वास घेण्यास त्रास शांत बसल्यावरही होतो की फक्त चालताना होतो?"
            },
            input_type=InputType.SINGLE_CHOICE,
            options=["Difficulty even at rest", "Difficulty only upon exertion/climbing stairs", "Difficulty lying flat", "No breathing difficulty"],
            next_default="past_medical_history"
        )

        # 5. Category Branch: Abdominal Pain pathway
        nodes["abdominal_details"] = QuestionNode(
            key="abdominal_details",
            prompts={
                "en": "Where exactly is the abdominal pain located (Upper, Lower right, Lower left, or all over)?",
                "hi": "पेट में दर्द ठीक किस जगह पर है (ऊपर, दाईं तरफ नीचे, बाईं तरफ या पूरे पेट में)?",
                "mr": "पोटात वेदना नक्की कुठे आहे (वर, उजव्या बाजूस खाली, डाव्या बाजूस की सर्व पोटात)?"
            },
            input_type=InputType.SINGLE_CHOICE,
            options=["Upper center (Epigastric / Gas)", "Right lower abdomen", "Left lower abdomen", "Diffused throughout abdomen"],
            next_default="past_medical_history"
        )

        # 6. Fallback General Symptom Duration & Severity
        nodes["symptom_duration"] = QuestionNode(
            key="symptom_duration",
            prompts={
                "en": "How long have you been experiencing this primary symptom?",
                "hi": "आप यह लक्षण कितने समय से महसूस कर रहे हैं?",
                "mr": "तुम्हाला हे लक्षण किती दिवसांपासून जाणवत आहे?"
            },
            input_type=InputType.SINGLE_CHOICE,
            options=["Started today (< 24 hours)", "2 to 3 days", "About 1 week", "More than 2 to 4 weeks (Chronic)"],
            next_default="symptom_severity"
        )
        nodes["symptom_severity"] = QuestionNode(
            key="symptom_severity",
            prompts={
                "en": "On a scale from 1 (mild discomfort) to 10 (unbearable agony), how severe is your symptom?",
                "hi": "1 (हल्की तकलीफ) से 10 (असहनीय दर्द) के पैमाने पर, आपकी तकलीफ कितनी गंभीर है?",
                "mr": "1 (हलका त्रास) ते 10 (असह्य वेदना) या श्रेणीवर, तुमचा त्रास किती तीव्र आहे?"
            },
            input_type=InputType.SCALE,
            options=["1 - 3 (Mild)", "4 - 6 (Moderate)", "7 - 8 (Severe)", "9 - 10 (Extreme / Unbearable)"],
            next_default="past_medical_history"
        )

        # 7. Common Medical History Questions
        nodes["past_medical_history"] = QuestionNode(
            key="past_medical_history",
            prompts={
                "en": "Do you have any diagnosed ongoing conditions like Diabetes, High BP, Asthma, Heart or Kidney disease?",
                "hi": "क्या आपको पहले से डायबिटीज, हाई बीपी, अस्थमा, हृदय या किडनी की बीमारी है?",
                "mr": "तुम्हाला आधीपासून मधुमेह, उच्च रक्तदाब, दमा, हृदय किंवा मूत्रपिंडाचा आजार आहे का?"
            },
            input_type=InputType.MULTI_CHOICE,
            options=["Diabetes (High Blood Sugar)", "Hypertension (High BP)", "Heart Disease", "Asthma / COPD", "Kidney Disease", "None of these"],
            next_default="current_medications"
        )
        nodes["current_medications"] = QuestionNode(
            key="current_medications",
            prompts={
                "en": "Are you currently taking any daily medicines or tablets? Please state names or upload your prescription in the next step.",
                "hi": "क्या आप वर्तमान में कोई नियमित दवाएं या गोलियां ले रहे हैं? कृपया नाम बताएं या अगले चरण में पर्ची स्कैन करें।",
                "mr": "तुम्ही सध्या काही नियमित औषधे किंवा गोळ्या घेत आहात का? कृपया नावे सांगा किंवा पुढील चरणात प्रिस्क्रिप्शन स्कॅन करा."
            },
            input_type=InputType.FREE_TEXT_OR_VOICE,
            options=["Taking BP / Diabetes medicines", "Taking pain killers or antibiotics", "Not taking any regular medicines"],
            next_default="allergies"
        )
        nodes["allergies"] = QuestionNode(
            key="allergies",
            prompts={
                "en": "Do you have any known allergies to medicines (like Penicillin, Sulfa, Aspirin) or specific foods?",
                "hi": "क्या आपको किसी दवा (जैसे पेनिसिलिन, सल्फा, एस्पिरिन) या विशेष खाद्य पदार्थ से एलर्जी है?",
                "mr": "तुम्हाला कोणत्याही औषधाची (पेनिसिलिन, सल्फा, ऍस्पिरिन) किंवा अन्नपदार्थाची ऍलर्जी आहे का?"
            },
            input_type=InputType.FREE_TEXT_OR_VOICE,
            options=["No known drug allergies", "Allergic to Penicillin", "Allergic to Sulfa drugs", "Other drug allergy"],
            next_default="intake_complete"
        )
        nodes["intake_complete"] = QuestionNode(
            key="intake_complete",
            prompts={
                "en": "Clinical questionnaire completed. Please proceed to scan any physical prescriptions or test reports.",
                "hi": "नैदानिक प्रश्नावली पूरी हुई। कृपया किसी भी पर्ची या परीक्षण रिपोर्ट को स्कैन करने के लिए आगे बढ़ें।",
                "mr": "प्रश्नावली पूर्ण झाली. कृपया कोणतीही कागदी प्रिस्क्रिप्शन किंवा तपासणी रिपोर्ट स्कॅन करण्यासाठी पुढे जा."
            },
            input_type=InputType.SINGLE_CHOICE,
            options=["Proceed to Document Scanner"],
            is_final=True
        )

        return nodes

    def _build_ayush_tree(self) -> Dict[str, QuestionNode]:
        nodes = {}

        # 1. AYUSH Chief Complaint
        nodes["chief_complaint_ayush"] = QuestionNode(
            key="chief_complaint_ayush",
            prompts={
                "en": "What is your main health concern or imbalance for visiting the AYUSH OPD?",
                "hi": "आयुष ओपीडी में आने का आपका मुख्य स्वास्थ्य कारण या अस्वस्थता क्या है?",
                "mr": "आयुष ओपीडीमध्ये येण्याचे तुमचे मुख्य आरोग्य कारण काय आहे?"
            },
            input_type=InputType.FREE_TEXT_OR_VOICE,
            options=["Digestive trouble (Gas / Acidity / Constipation)", "Joint stiffness / Vata disorder", "Skin condition / Itching", "Stress / Insomnia / Fatigue", "Respiratory / Kapha imbalance", "General health checkup"],
            next_default="agni_digestion"
        )

        # 2. Agni & Digestion (Jatharagni assessment)
        nodes["agni_digestion"] = QuestionNode(
            key="agni_digestion",
            prompts={
                "en": "How is your appetite and digestion (Agni)?",
                "hi": "आपकी भूख और पाचन शक्ति (अग्नि) कैसी है?",
                "mr": "तुमची भूक आणि पचनशक्ती (अग्नि) कशी आहे?"
            },
            input_type=InputType.SINGLE_CHOICE,
            options=[
                "Manda Agni (Low appetite, heavy stomach after meals)",
                "Tikshna Agni (Excess hunger, burning acidity)",
                "Vishama Agni (Irregular hunger, variable digestion)",
                "Sama Agni (Healthy balanced digestion)"
            ],
            next_default="koshta_bowel"
        )

        # 3. Koshta (Bowel movements)
        nodes["koshta_bowel"] = QuestionNode(
            key="koshta_bowel",
            prompts={
                "en": "How are your bowel habits (Koshta)?",
                "hi": "पेट साफ होने की आदत (कोष्ठ) कैसी है?",
                "mr": "पोट साफ होण्याची सवय (कोष्ठ) कशी आहे?"
            },
            input_type=InputType.SINGLE_CHOICE,
            options=[
                "Krura Koshta (Hard stools, constipation, straining)",
                "Mridu Koshta (Loose or frequent motions)",
                "Madhyama Koshta (Regular, smooth daily evacuation)"
            ],
            next_default="nidra_sleep"
        )

        # 4. Nidra & Manas (Sleep and mental stress)
        nodes["nidra_sleep"] = QuestionNode(
            key="nidra_sleep",
            prompts={
                "en": "How is your sleep pattern (Nidra) and stress level?",
                "hi": "आपकी नींद (निद्रा) और मानसिक तनाव का स्तर कैसा है?",
                "mr": "तुमची झोप (निद्रा) आणि तणाव कसा आहे?"
            },
            input_type=InputType.SINGLE_CHOICE,
            options=[
                "Disturbed, light sleep, difficulty falling asleep (Vata)",
                "Sound sleep but waking up with night sweats/heat (Pitta)",
                "Excessive heavy sleep, waking up tired (Kapha)",
                "Normal restful 6-8 hours sleep"
            ],
            next_default="prakriti_features"
        )

        # 5. Prakriti physical characteristics
        nodes["prakriti_features"] = QuestionNode(
            key="prakriti_features",
            prompts={
                "en": "Which physical traits best describe your body constitution (Prakriti)?",
                "hi": "कौन सी शारीरिक विशेषताएं आपकी प्रकृति से सबसे मेल खाती हैं?",
                "mr": "कोणती शारीरिक लक्षणे तुमच्या प्रकृतीशी जुळतात?"
            },
            input_type=InputType.SINGLE_CHOICE,
            options=[
                "Dry skin, lean frame, sensitive to cold (Vata)",
                "Warm body, reddish skin, sensitive to heat (Pitta)",
                "Thick skin, solid/heavy build, slow metabolism (Kapha)",
                "Mixed constitution"
            ],
            next_default="ayush_medications"
        )

        # 6. Current Medications (Allopathic & Ayurvedic)
        nodes["ayush_medications"] = QuestionNode(
            key="ayush_medications",
            prompts={
                "en": "Are you currently taking any Ayurvedic, Homeopathic, or Allopathic medications?",
                "hi": "क्या आप वर्तमान में कोई आयुर्वेदिक, होम्योपैथिक या एलोपैथिक दवाएं ले रहे हैं?",
                "mr": "तुम्ही सध्या काही आयुर्वेदिक, होमिओपॅथिक किंवा ॲलोपॅथिक औषधे घेत आहात का?"
            },
            input_type=InputType.FREE_TEXT_OR_VOICE,
            options=["Taking Ayurvedic formulations / Kadha", "Taking Allopathic BP/Sugar tablets", "Taking Homeopathic remedies", "Not taking any medications"],
            next_default="ayush_complete"
        )

        # 7. AYUSH Final
        nodes["ayush_complete"] = QuestionNode(
            key="ayush_complete",
            prompts={
                "en": "AYUSH intake questionnaire completed. Proceed to scan any past prescriptions or lab tests.",
                "hi": "आयुष प्रश्नावली पूरी हुई। कृपया पिछली पर्ची या रिपोर्ट स्कैन करने के लिए आगे बढ़ें।",
                "mr": "आयुष प्रश्नावली पूर्ण झाली. कृपया मागील प्रिस्क्रिप्शन किंवा रिपोर्ट स्कॅन करण्यासाठी पुढे जा."
            },
            input_type=InputType.SINGLE_CHOICE,
            options=["Proceed to Document Scanner"],
            is_final=True
        )

        return nodes

    def get_next_question(
        self,
        mode: ClinicalMode,
        previous_answers: List[PreviousAnswer],
        language: str = "en"
    ) -> NextQuestionResponse:
        """
        Dynamically determine the next question based on triage mode and answered history.
        """
        tree = self.ayush_nodes if mode == ClinicalMode.AYUSH else self.allopathic_nodes
        root_key = "chief_complaint_ayush" if mode == ClinicalMode.AYUSH else "chief_complaint"

        if not previous_answers:
            first_node = tree[root_key]
            return NextQuestionResponse(
                question_key=first_node.key,
                question_text=first_node.get_prompt(language),
                input_type=first_node.input_type,
                options=first_node.options,
                is_final=first_node.is_final
            )

        # Analyze chief complaint to select specialized branch if in Allopathic mode
        answered_keys = {ans.question_key: ans.answer_text for ans in previous_answers}
        last_answer = previous_answers[-1]

        # Branching logic for Chief Complaint
        if last_answer.question_key == "chief_complaint":
            cc_text = last_answer.answer_text.lower()
            if any(w in cc_text for w in ["fever", "bukhar", "temperature", "chills", "taap"]):
                next_key = "fever_duration"
            elif any(w in cc_text for w in ["chest", "cardiac", "heart", "sinha", "seena"]):
                next_key = "chest_pain_character"
            elif any(w in cc_text for w in ["cough", "breath", "khansi", "phlegm", "asthma", "dam"]):
                next_key = "cough_details"
            elif any(w in cc_text for w in ["stomach", "abdom", "pet", "belly", "gastric"]):
                next_key = "abdominal_details"
            else:
                next_key = "symptom_duration"
        else:
            current_node = tree.get(last_answer.question_key)
            if current_node and current_node.next_default:
                next_key = current_node.next_default
            else:
                next_key = "intake_complete" if mode == ClinicalMode.ALLOPATHIC else "ayush_complete"

        # Check if requested node was already answered; if so, advance to next unfulfilled mandatory question
        candidate_node = tree.get(next_key)
        if not candidate_node or candidate_node.key in answered_keys:
            # Look for unvisited mandatory steps
            if mode == ClinicalMode.ALLOPATHIC:
                mandatory_sequence = ["past_medical_history", "current_medications", "allergies", "intake_complete"]
            else:
                mandatory_sequence = ["agni_digestion", "koshta_bowel", "nidra_sleep", "prakriti_features", "ayush_medications", "ayush_complete"]

            for step in mandatory_sequence:
                if step not in answered_keys:
                    candidate_node = tree.get(step)
                    break
            else:
                final_key = "intake_complete" if mode == ClinicalMode.ALLOPATHIC else "ayush_complete"
                candidate_node = tree[final_key]

        return NextQuestionResponse(
            question_key=candidate_node.key,
            question_text=candidate_node.get_prompt(language),
            input_type=candidate_node.input_type,
            options=candidate_node.options,
            is_final=candidate_node.is_final
        )
