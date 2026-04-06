import os
from dotenv import load_dotenv
from google import genai
import gradio as gr
from reportlab.lib.pagesizes import letter
from reportlab.pdfgen import canvas
from reportlab.lib.pagesizes import letter

# Cargar variables
load_dotenv()

# Cliente Gemini
client = genai.Client(api_key=os.getenv("GEMINI_API_KEY"))

def generar_plan(nivel, molestias, objetivo):
    if not nivel:
        return "Debes seleccionar un nivel."

    if not molestias:
        molestias = "ninguna"

    prompt = f"""
    Actúa como un entrenador profesional de CrossFit.

    Usuario:
    - Nivel: {nivel}
    - Molestias: {molestias}
    - Objetivo: {objetivo}

    Genera un plan de entrenamiento de 5 días.

    Formato obligatorio:

    Día 1:
    - Calentamiento:
    - Parte principal:
    - WOD:

    Día 2:
    ...

    Reglas:
    - Ajusta intensidad según nivel
    - Si hay molestias, adapta ejercicios
    - Usa lenguaje claro
    - No expliques teoría, solo el plan
    - El entrenamiento debe ser integral pero con énfasis en el objetivo del usuario
    """

    response = client.models.generate_content(
        model="gemini-2.0-flash",
        contents=prompt
    )

    plan_texto = response.text

    # Validar el plan
    validacion = validar_plan(plan_texto, molestias)
    # Si hay error, corregir el plan
    if "ERROR" in validacion:
        plan_final = corregir_plan(plan_texto, molestias)
    else:
        plan_final = plan_texto

    pdf_path = crear_pdf(plan_final)

    return plan_final, pdf_path
def crear_pdf(texto):
    file_path = "plan_entrenamiento.pdf"
    c = canvas.Canvas(file_path, pagesize=letter)
    max_width = 90  # caracteres por línea aprox
    y_start = 750
    line_height = 12
    x_margin = 40
    y = y_start

    for line in texto.split("\n"):
        # dividir líneas largas
        while len(line) > max_width:
            fragment = line[:max_width]
            c.drawString(x_margin, y, fragment)
            line = line[max_width:]
            y -= line_height
            if y < 40:  # crear nueva página si llegamos al fondo
                c.showPage()
                y = y_start

        # escribir línea restante
        c.drawString(x_margin, y, line)
        y -= line_height
        if y < 40:
            c.showPage()
            y = y_start

    c.save()

    return file_path
def validar_plan(plan, molestias):
    prompt = f"""
    Actúa como un experto en entrenamiento y lesiones.

    Revisa el siguiente plan de entrenamiento y determina si respeta las molestias del usuario.

    Molestias del usuario: {molestias}

    Plan:
    {plan}

    Responde SOLO con:
    - "OK" si el plan es adecuado
    - "ERROR" si el plan incluye ejercicios que podrían empeorar la molestia
    - Si es ERROR, explica brevemente por qué
    """

    response = client.models.generate_content(
        model="gemini-2.0-flash",
        contents=prompt
    )

    return response.text
def corregir_plan(plan, molestias):
    prompt = f"""
    Actúa como un entrenador experto en rehabilitación y CrossFit.

    El siguiente plan es INCORRECTO porque incluye ejercicios que pueden empeorar la molestia del usuario.

    Molestias: {molestias}

    Plan original:
    {plan}

    Tu tarea es CREAR UN NUEVO PLAN desde cero (no modificar parcialmente).

    Reglas estrictas:
    - PROHIBIDO incluir ejercicios que generen impacto o estrés en la zona afectada
    - Si la molestia es rodilla: NO usar sentadillas profundas, lunges, saltos, burpees, running, box jumps
    - Usa alternativas seguras (ej: trabajo de tren superior, core, ejercicios controlados)
    - Mantener estructura de 5 días
    - Cada día debe tener: calentamiento, parte principal y WOD
    - El entrenamiento debe seguir siendo efectivo

    Devuelve SOLO el nuevo plan corregido completo.
    """

    response = client.models.generate_content(
        model="gemini-2.0-flash",
        contents=prompt
    )

    return response.text
# Interfaz Gradio
interfaz = gr.Interface(
    fn=generar_plan,
    inputs=[
    gr.Dropdown(
        choices=["principiante", "intermedio", "avanzado"],
        label="Nivel de CrossFit"
    ),
    gr.Textbox(label="Molestias o lesiones", placeholder="Ej: dolor de rodilla, hombro, etc."),
    gr.Textbox(label="Objetivo", placeholder="Ej: mejorar piernas, glúteos, fuerza general, etc.")
],
    outputs=[
    gr.Textbox(label="Plan de entrenamiento"),
    gr.File(label="Descargar PDF")],
    title="Agente de Entrenamiento CrossFit",
    description="Genera un plan personalizado de 5 días basado en tu nivel y molestias"
)

if __name__ == "__main__":
    interfaz.launch()
