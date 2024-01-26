def generate_html(application, computer_skills, experiences, language_skills, educations, applicant_docs, test_result=None):

    computer_skills_string = ""
    for computer_skill in computer_skills:
        computer_skills_string = f"""
                    <ul class="list">
                        <li>Id - {computer_skill.id}</li>
                        <li>Name - {computer_skill.name}</li>
                        <li>Degree - {computer_skill.degree}</li>
                    </ul>
                    """

    experiences_string = ""
    for experience in experiences:
        experiences_string = f"""
                    <ul class="list">
                        <li>ID - {experience.id}</li>
                        <li>Organization name - {experience.organization_name}</li>
                        <li>Organization address - {experience.organization_address}</li>
                        <li>Position - {experience.position}</li>
                        <li>Started date - {experience.started_date}</li>
                        <li>Finished date - {experience.finished_date}</li>
                        <li>Country - {experience.country}</li>
                    </ul>
                    """

    educations_string = ""
    for education in educations:
        educations_string = f"""
                    <ul class="list">
                        <li>ID - {education.id}</li>
                        <li>Education Name - {education.title}</li>
                        <li>Started date - {education.started_date}</li>
                        <li>Finished date - {education.finished_date}</li>
                        <li>Direction - {education.direction}</li>
                        <li>Country - {education.country}</li>
                    </ul>
                    """

    language_skills_string = ""
    for language_skill in language_skills:
        language_skills_string = f"""
                    <ul class="list">
                        <li>ID - {language_skill.id}</li>
                        <li>Langauge Name - {language_skill.name}</li>
                        <li>Speaking - {language_skill.speaking}</li>
                        <li>Reading - {language_skill.reading}</li>
                        <li>Writing - {language_skill.writing}</li>
                        <li>Listening - {language_skill.listening}</li>
                        
                    </ul>
                    """
    applicant_docs_string = ""
    for applicant_doc in applicant_docs:
        applicant_docs_string = f"""
                    <ul class="documents-list">
                        <li>ID - {applicant_doc.id}</li>
                        <li>File - http://143.110.145.222/media{applicant_doc.file}</li>
                        <li>Type - {applicant_doc.type}</li>
                    </ul>
                    """
    if test_result:
        test_result_string = f"""
                     <ul class="list">
                        <li>Total ball - {test_result.total_ball} ball</li>
                        <li>Test - {test_result.test}</li>
                        <li>Test date - {test_result.finished_at}</li>
                    </ul>
                    """
    else:
        test_result_string = "Test has not been passed yet"
    html_content = f"""
        <!DOCTYPE html>
        <html lang="en">
        <head>
            <meta charset="UTF-8">
            <meta name="viewport" content="width=device-width, initial-scale=1.0">
            <title>Applicant Information</title>
            
        </head>
        <body>
        
            <div class="container">
                <h2>Applicant Information</h2>
        
                <div class="image-section">
                    <h2>Applicant Image</h2>
                    <div class="image-placeholder">
                    <img src="http://143.110.145.222{application.user_photo.url}" alt="Description of the image"></div>
                </div>
        
                <dl>
                    <dt>First name:</dt>
                    <dd>{application.first_name}</dd>
        
                    <dt>Last name:</dt>
                    <dd>{application.last_name}</dd>
        
                    <dt>Height:</dt>
                    <dd>{application.height}</dd>
        
                    <dt>Weight:</dt>
                    <dd>{application.weight}</dd>
        
                    <dt>Phone number:</dt>
                    <dd>{application.phone_number}</dd>
        
                    <dt>Email:</dt>
                    <dd>{application.email}</dd>
        
                    <dt>Family status:</dt>
                    <dd>{application.family_status}</dd>
        
                    <dt>Birth date:</dt>
                    <dd>{application.birth_date}</dd>
        
                    <dt>Address:</dt>
                    <dd>{application.address}</dd>
        
                    <dt>Requested position:</dt>
                    <dd>{application.requested_position}</dd>
                </dl>
        
                <div class="section">
                    <h2>Computer Skills</h2>
                    {computer_skills_string}
                </div>
        
                <div class="section">
                    <h2>Experiences</h2>
                    {experiences_string}
                </div>
        
                <div class="section">
                    <h2>Educations</h2>
                    {educations_string}
                    
                </div>
        
                <div class="section">
                    <h2>Language Skills</h2>
                    {language_skills_string}
                </div>
        
                <div class="section documents-section">
                    <h2>Applicant Docs</h2>
                    {applicant_docs_string}
                </div>
                
                <div class="section">
                    <h2>Test Result</h2>
                    {test_result_string}
                </div>
            </div>
        
        </body>
        </html>
    """
    html_content = html_content.format(
        application=application,
        computer_skills=computer_skills,
        experiences=experiences,
        language_skills=language_skills,
        educations=educations,
        applicant_docs=applicant_docs,

    )
    with open('bot/templates/applicant_info.html', 'w') as file:
        file.write(html_content)
