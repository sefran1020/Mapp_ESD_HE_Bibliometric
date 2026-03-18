# Criterios de Inclusión, Exclusión y Métricas de Evaluación

Basado en el análisis de las justificaciones de los revisores en el archivo `seleccionados80.csv` (Lead Methodologist, ESD & Sustainability Education Expert, y Climate Literacy & Green Skills Specialist) y los reportes de métricas adjuntos (`reliability_metrics.csv` y `disagreement_report.csv`), se establecen los siguientes criterios y métricas para el proceso de screening.

## 1. Criterios de Inclusión (Acuerdo de la Estrategia PICO)

Para que un artículo sea considerado **INCLUDE (INCLUIDO)**, debe cumplir satisfactoriamente con los siguientes cuatro criterios (CUMPLE o PARCIAL justificado):

*   **Population (P-HEI Context)**: El estudio debe estar situado en Instituciones de Educación Superior (IES/HEI), involucrando como población a estudiantes universitarios (pregrado, posgrado), docentes, profesores en formación (pre-service teachers) o facultades dentro del contexto de educación terciaria.
*   **Intervention (I-ESD Framework)**: El estudio debe abordar la integración, aplicación o diseño de currículos, estrategias pedagógicas u organizacionales vinculadas a la Educación para el Desarrollo Sostenible (ESD), la alfabetización climática (Climate Literacy) o el desarrollo de competencias/habilidades verdes (Green Skills).
*   **Comparison (C-Comparison)**: El estudio debe contemplar elementos que permitan un análisis comparativo, ya sea explícito o implícito. Esto incluye pruebas pre/post test en intervenciones educativas, comparaciones geográficas transversales (entre países/regiones), institucionales, demográficas, o análisis comparativo de perspectivas e ideologías sobre la sostenibilidad. (Es frecuente que los revisores evalúen este punto como PARCIAL si no hay un grupo de control formal pero se incluye algún nivel de análisis interno iterativo o longitudinal).
*   **Outcome (O-Outcome)**: El estudio debe presentar resultados medibles o evaluables respecto al desarrollo e integración de competencias de sostenibilidad (conocimientos, actitudes, valores, modificación de comportamiento, disposición hacia pro-ambientalismo) o transformación institucional (greening curriculum y estrategias de evaluación).
*   **Rango de Tiempo e Idioma**: El artículo debe pertenecer al periodo post-adopción de la Agenda 2030 (publicado de 2015 en adelante) y estar redactado en base a investigación primaria (estudio empírico de tipo cualitativo, cuantitativo, mixto o estudio de caso práctico).

---

## 2. Criterios de Exclusión

Un artículo se cataloga como **EXCLUDE (EXCLUIDO)** si incumple uno o varios de los puntos metodológicos centrales:

*   **Contexto no perteneciente a la Educación Superior**: Estudios centrados exclusivamente en educación primaria, secundaria o enfocados únicamente en el público general sin vínculo a la Educación Superior o formación docente universitaria.
*   **Desalineación de la Intervención**: Estudios que, aunque hablan de sostenibilidad o medio ambiente, no presentan un enfoque, marco de intervención pedagógica o de desarrollo de resiliencia orientada a la Educación para el Desarrollo Sostenible (ESD) o competencias afines en la educación.
*   **Carencia de Resultados Relacionados a Sostenibilidad / Competencias**: Ausencia de resultados en la formación de habilidades, actitudes o conocimiento de sustentabilidad en los sujetos de estudio; o artículos puramente conceptuales o de desarrollo de infraestructuras técnicas sostenibles donde el sistema educativo no sea el factor principal de intervención/análisis.

---

## 3. Métricas de Evaluación y Confiabilidad

El análisis de la carpeta `output` (`seleccionados80.csv`, `reliability_metrics.csv`, `disagreement_report.csv`) revela una estructura algorítmica y de consenso donde el proceso se apoya en tres revisores que aplican reglas estrictas sobre el formato PICO. Las métricas utilizadas son:

*   **Decisión Individual y Confianza (`reviewer_decision` / `reviewer_confidence`)**: Cada revisor (Role 1: Lead Methodologist, Role 2: ESD Expert, Role 3: Climate Literacy Specialist) emite un voto categórico (`INCLUDE`, `EXCLUDE`, o `UNCERTAIN`) validado por una puntuación justificada texto a texto de los elementos PICO, asignando un nivel de confianza (típicamente entre 0-100%).
*   **Nivel de Concordancia (`concordance_level`)**: Determina el nivel de acuerdo del tribunal de revisión. Ejemplos de categorización:
    *   *Unanimous*: Todos los revisores llegaron a la misma conclusión (e.g., 3 INCLUDES).
    *   *Partial / Mayoría*: Dos revisores en una dirección, uno en discrepancia (e.g., INCLUDE(2) vs EXCLUDE(1)).
*   **Métricas Globales de Confiabilidad (`reliability_metrics.csv`)**: Cuantifican el acuerdo estadístico entre revisores:
    *   **Porcentaje de Acuerdo (Percent Agreement)**: Ratio general de consenso (e.g., ~71-76%).
    *   **Kappa de Fleiss (`fleiss_kappa`)**: Evalúa la fiabilidad del acuerdo inter-jueces general en múltiples categorías. (Los valores promedio oscilan entre moderados y sustanciales, e.g., ~0.52 - 0.68).
    *   **Kappa de Cohen Parcial (`cohens_kappa`)**: Evalúa el grado de acuerdo bidireccional entre pares de clasificadores (ej. entre el Rol 1 y 2, que suele reportar un valor fuerte de ~0.79).
    *   **ICC (Coeficiente de Correlación Intraclase)**: Para medir la consistencia del grado de confianza.
    *   **Kappas por Categoría (`category_kappa_include`, `category_kappa_exclude`)**: Cuantifican la fiabilidad con la que los revisores logran acuerdo específicamente para aceptar o rechazar un artículo, donde suelen verse puntuaciones de acuerdo fuerte a moderado (~0.5 - 0.7).
*   **Puntuación Final (`score_final`)**: Un cálculo de score compuesto (ej. `0.805 - 0.856`) determinado por las confianzas promedios y la sumatoria del peso de decisiones que ratifican numéricamente la relevancia del estudio y legitimizan la clasificación (e.g., pasando de "observacion" a "incluido" automático o requiriendo resolución de árbitro humano en caso de discrepancias serias con confianza baja).
