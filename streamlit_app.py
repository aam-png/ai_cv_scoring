import streamlit as st
from openai import OpenAI
from parse_hh import get_html, extract_vacancy_data, extract_resume_data

st.set_page_config(page_title="CV Scoring App", page_icon="✅", layout="centered")
st.title("CV Scoring App")

# OPENAI
try:
    client = OpenAI(api_key=st.secrets["OPENAI_API_KEY"])
except Exception:
    st.error("❗ Не найден OPENAI_API_KEY в .streamlit/secrets.toml")
    st.stop()

SYSTEM_PROMPT = """
Проскорь кандидата, насколько он подходит для данной вакансии.
Сначала напиши короткий анализ, который будет пояснять оценку.
Отдельно оцени качество заполнения резюме (понятно ли, с какими задачами сталкивался кандидат и каким образом их решал?).
Эта оценка должна учитываться при выставлении финальной оценки.
Потом представь результат в виде оценки от 1 до 10.
""".strip()

def request_gpt(system_prompt: str, user_prompt: str) -> str:
    resp = client.chat.completions.create(
        model="gpt-4o-mini",
        messages=[
            {"role": "system", "content": system_prompt},
            {"role": "user", "content": user_prompt},
        ],
        temperature=0,
        max_tokens=1200,
    )
    return resp.choices[0].message.content

# ---- UI ----
mode = st.tabs(["По ссылкам", "Вставить текст вручную"])

with mode[0]:
    st.subheader("Ссылки для анализа")
    job_url = st.text_input("Ссылка на вакансию")
    resume_url = st.text_input("Ссылка на резюме")

    if st.button("Проанализировать (по ссылкам)"):
        if not job_url.strip() or not resume_url.strip():
            st.warning("⚠️ Укажите обе ссылки.")
        else:
            with st.spinner("Парсим страницы и оцениваем..."):
                try:
                    job_html = get_html(job_url)
                    resume_html = get_html(resume_url)
                    job_text = extract_vacancy_data(job_html)
                    resume_text = extract_resume_data(resume_html)

                    prompt = f"# ВАКАНСИЯ\n{job_text}\n\n# РЕЗЮМЕ\n{resume_text}"
                    result = request_gpt(SYSTEM_PROMPT, prompt)

                    st.subheader("📄 Извлечённая вакансия")
                    st.markdown(job_text)
                    st.subheader("👤 Извлечённое резюме")
                    st.markdown(resume_text)
                    st.subheader("📊 Результат анализа")
                    st.markdown(result)

                    st.download_button(
                        "Скачать результат (Markdown)",
                        data=f"{job_text}\n\n{resume_text}\n\n---\n\n{result}",
                        file_name="cv_scoring_result.md",
                        mime="text/markdown",
                    )
                except Exception as e:
                    st.error(f"Ошибка: {e}")

with mode[1]:
    st.subheader("Вставьте тексты вручную")
    job_text_manual = st.text_area("Текст вакансии", height=200)
    resume_text_manual = st.text_area("Текст резюме", height=200)

    if st.button("Проанализировать (вставленный текст)"):
        if not job_text_manual.strip() or not resume_text_manual.strip():
            st.warning("⚠️ Заполните оба поля.")
        else:
            with st.spinner("Оцениваем..."):
                try:
                    prompt = f"# ВАКАНСИЯ\n{job_text_manual}\n\n# РЕЗЮМЕ\n{resume_text_manual}"
                    result = request_gpt(SYSTEM_PROMPT, prompt)

                    st.subheader("📊 Результат анализа")
                    st.markdown(result)

                    st.download_button(
                        "Скачать результат (Markdown)",
                        data=f"{job_text_manual}\n\n{resume_text_manual}\n\n---\n\n{result}",
                        file_name="cv_scoring_result.md",
                        mime="text/markdown",
                    )
                except Exception as e:
                    st.error(f"Ошибка: {e}")