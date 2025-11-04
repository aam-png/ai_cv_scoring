import requests
from bs4 import BeautifulSoup

UA = (
    "Mozilla/5.0 (Windows NT 10.0; Win64; x64) "
    "AppleWebKit/537.36 (KHTML, like Gecko) "
    "Chrome/123.0.0.0 Safari/537.36"
)

def get_html(url: str) -> str:
    resp = requests.get(url, headers={"User-Agent": UA}, timeout=20)
    resp.raise_for_status()
    resp.encoding = resp.apparent_encoding
    return resp.text

# -------- ВАКАНСИЯ --------
def extract_vacancy_data(html: str) -> str:
    soup = BeautifulSoup(html, "html.parser")

    def txt(sel, attrs=None, default="Не найдено"):
        el = soup.find(sel, attrs or {})
        return el.get_text(separator="\n", strip=True) if el else default

    title = txt("h1")
    company = txt("a", {"data-qa": "vacancy-company-name"})
    salary = txt("span", {"data-qa": "vacancy-salary"})
    descr_el = soup.find("div", {"data-qa": "vacancy-description"})
    description = descr_el.get_text(separator="\n", strip=True) if descr_el else "Описание не найдено"

    md = f"# {title}\n\n"
    md += f"**Компания:** {company}\n\n"
    md += f"**Зарплата:** {salary}\n\n"
    md += f"## Описание\n\n{description}"
    return md.strip()

# -------- РЕЗЮМЕ --------
def extract_resume_data(html: str) -> str:
    soup = BeautifulSoup(html, "html.parser")

    def tx(el):
        return el.get_text(separator="\n", strip=True) if el else "Не найдено"

    name = tx(soup.find("h2", {"data-qa": "bloko-header-1"}))
    gender_age = tx(soup.find("p"))
    location = tx(soup.find("span", {"data-qa": "resume-personal-address"}))
    job_title = tx(soup.find("span", {"data-qa": "resume-block-title-position"}))
    job_status = tx(soup.find("span", {"data-qa": "job-search-status"}))

    experiences_md = []
    exp_block = soup.find("div", {"data-qa": "resume-block-experience"})
    if exp_block:
        for item in exp_block.find_all("div", class_="resume-block-item-gap"):
            try:
                period = tx(item.find("div", class_="bloko-column_s-2"))
                duration = tx(item.find("div", class_="bloko-text"))
                if duration != "Не найдено" and period.endswith(duration) is False:
                    period = f"{period} ({duration})"
                company = tx(item.find("div", class_="bloko-text_strong"))
                position = tx(item.find("div", {"data-qa": "resume-block-experience-position"}))
                description = tx(item.find("div", {"data-qa": "resume-block-experience-description"}))
                experiences_md.append(f"**{period}**\n\n*{company}*\n\n**{position}**\n\n{description}\n")
            except Exception:
                continue

    skills_list = []
    skills_section = soup.find("div", {"data-qa": "skills-table"})
    if skills_section:
        skills_list = [tx(tag) for tag in skills_section.find_all("span", {"data-qa": "bloko-tag__text"})]

    md = f"# {name}\n\n"
    md += f"**{gender_age}**\n\n"
    md += f"**Местоположение:** {location}\n\n"
    md += f"**Должность:** {job_title}\n\n"
    md += f"**Статус:** {job_status}\n\n"
    md += "## Опыт работы\n\n"
    md += ("\n".join(experiences_md) if experiences_md else "Опыт работы не найден.\n")
    md += "\n## Ключевые навыки\n\n"
    md += (", ".join(skills_list) if skills_list else "Навыки не указаны.\n")
    return md.strip()
