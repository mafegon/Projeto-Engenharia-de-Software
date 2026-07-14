from datetime import date

from django.db import migrations


COURSES = (("cc", "Ciência da Computação"), ("ee", "Engenharia Elétrica"),
           ("adm", "Administração"), ("jor", "Jornalismo"), ("bio", "Ciências Biológicas"))

INTERNSHIPS = (
    ("prodap", "PRODAP — Centro de Gestão da TIC do Amapá", "PRODAP", "00.000.001/0001-01", "Estágio em Desenvolvimento Web", "Centro, Macapá", "Tecnologia da Informação", "hybrid", 30, "R$ 1.000/mês", "Atuação na construção e manutenção de aplicações web em Python, Django e PostgreSQL.", ["Lógica de programação e banco de dados", "Python", "HTML, CSS e Git"], ["cc"], 4, date(2027, 7, 31)),
    ("cea", "CEA Equatorial", "CEA", "00.000.002/0001-02", "Estágio em Engenharia Elétrica", "Santa Rita, Macapá", "Engenharia", "onsite", 30, "R$ 1.100/mês", "Apoio às atividades de engenharia elétrica e manutenção.", ["Fundamentos de engenharia elétrica"], ["ee"], 3, date(2027, 8, 15)),
    ("tjap", "Tribunal de Justiça do Amapá", "TJAP", "00.000.003/0001-03", "Estágio em Comunicação Social", "Centro, Macapá", "Comunicação", "onsite", 20, "R$ 850/mês", "Apoio à comunicação institucional e produção de conteúdo.", ["Boa comunicação escrita"], ["jor"], 3, date(2027, 8, 15)),
    ("basa", "Banco da Amazônia", "BASA", "00.000.004/0001-04", "Estágio em Análise de Dados", "Remoto", "Tecnologia da Informação", "remote", 20, "R$ 900/mês", "Apoio à análise de dados e construção de indicadores.", ["Lógica de programação", "Planilhas"], ["cc"], 3, date(2027, 8, 31)),
    ("sebrae", "SEBRAE Amapá", "SEBRAE", "00.000.005/0001-05", "Estágio em Administração", "Trem, Macapá", "Administração", "onsite", 30, "R$ 800/mês", "Apoio a processos administrativos e atendimento.", ["Organização", "Comunicação"], ["adm"], 2, date(2027, 8, 31)),
    ("iepa", "IEPA — Instituto de Pesquisas do Amapá", "IEPA", "00.000.006/0001-06", "Estágio em Meio Ambiente", "Fazendinha, Macapá", "Meio Ambiente", "onsite", 20, "R$ 750/mês", "Apoio a pesquisas e atividades de campo na área ambiental.", ["Interesse em pesquisa de campo"], ["bio"], 3, date(2027, 8, 31)),
)


def seed_catalog(apps, schema_editor):
    Account = apps.get_model("platform_api", "Account")
    Company = apps.get_model("platform_api", "Company")
    Course = apps.get_model("platform_api", "Course")
    Internship = apps.get_model("platform_api", "Internship")
    InternshipCourse = apps.get_model("platform_api", "InternshipCourse")
    for code, name in COURSES:
        Course.objects.get_or_create(code=code, defaults={"name": name})
    for item in INTERNSHIPS:
        (slug, legal_name, trade_name, cnpj, title, location, area, modality,
         weekly_hours, stipend, description, requirements, course_codes,
         minimum_semester, deadline) = item
        account, _ = Account.objects.get_or_create(
            email=f"demo-{slug}@estagios.invalid", defaults={"password_hash": "!demo-account-disabled"}
        )
        company, _ = Company.objects.get_or_create(
            cnpj=cnpj,
            defaults={"account_id": account.pk, "legal_name": legal_name, "trade_name": trade_name,
                      "phone": "", "address": location, "about": "Organização de demonstração."},
        )
        internship, _ = Internship.objects.get_or_create(
            slug=slug,
            defaults={"company_id": company.pk, "title": title, "location": location, "area": area,
                      "modality": modality, "weekly_hours": weekly_hours, "stipend": stipend,
                      "description": description, "requirements": requirements,
                      "minimum_semester": minimum_semester, "application_deadline": deadline,
                      "external_application": False, "external_url": "", "status": "ativa"},
        )
        for course_code in course_codes:
            InternshipCourse.objects.get_or_create(
                internship_id=internship.pk, course_id=course_code
            )


class Migration(migrations.Migration):
    dependencies = [("platform_api", "0001_initial")]
    operations = [migrations.RunPython(seed_catalog, migrations.RunPython.noop)]
