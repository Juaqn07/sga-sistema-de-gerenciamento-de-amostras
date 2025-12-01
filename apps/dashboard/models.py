from django.db import models

# NOTA DE ARQUITETURA:
# Este app não possui modelos próprios.
# Ele atua como uma camada de visualização (View Layer), agregando e processando
# dados dos modelos 'Processo' (app samples) e 'Usuario' (app accounts).
