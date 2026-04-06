import os
from dotenv import load_dotenv
from google import genai
import gradio as gr
from reportlab.lib.pagesizes import letter
from reportlab.pdfgen import canvas

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

    pdf_path = crear_pdf(plan_texto)

    return plan_texto, pdf_path
def crear_pdf(texto):
    file_path = "plan_entrenamiento.pdf"
    c = canvas.Canvas(file_path, pagesize=letter)

    textobject = c.beginText(40, 750)
    textobject.setFont("Helvetica", 10)

    max_width = 90  # caracteres por línea aprox

    for line in texto.split("\n"):
        while len(line) > max_width:
            textobject.textLine(line[:max_width])
            line = line[max_width:]
        textobject.textLine(line)

    c.drawText(textobject)
    c.save()

    return file_path
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
