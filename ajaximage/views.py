# -*- coding: utf-8 -*-

import os
import json
import re

from PIL import Image
from easy_thumbnails.files import get_thumbnailer
from unicodedata import normalize

from django.conf import settings
from django.contrib.admin.templatetags.admin_static import static
from django.contrib.admin.views.decorators import staff_member_required
from django.core.files.storage import default_storage
from django.http import HttpResponse
from django.utils.text import slugify
from django.views.decorators.csrf import csrf_exempt
from django.views.decorators.http import require_POST

from .image import resize
from .forms import FileForm


UPLOAD_PATH = getattr(
        settings, 'AJAXIMAGE_DIR', 'ajaximage/')
AUTH_TEST = getattr(
        settings, 'AJAXIMAGE_AUTH_TEST', lambda u: u.is_staff)
FILENAME_NORMALIZER = getattr(
        settings, 'AJAXIMAGE_FILENAME_NORMALIZER', slugify)


@csrf_exempt
@require_POST
@staff_member_required
def ajaximage(request, upload_to=None, max_width=None, max_height=None,
              crop=None, form_class=FileForm, response=lambda name, url: url):

    form = form_class(request.POST, request.FILES)

    if form.is_valid():

        file_ = form.cleaned_data['file']

        image_types = ['image/png', 'image/jpg', 'image/jpeg', 'image/pjpeg',
                       'image/gif']

        if file_.content_type not in image_types:
            return HttpResponse(status=403,
                                content='Formato da imagem inválido!')

        #IOError: cannot write mode P as JPEG#
        tmp_image = Image.open(file_)
        if tmp_image.mode != 'RGB':
            tmp_image = tmp_image.convert('RGB')
            file_.seek(0)
            tmp_image.save(file_, 'jpeg')
        file_.seek(0)

        file_ = resize(file_, max_width, max_height, crop)

        #remove acentuação#
        nome_arquivo = normalize('NFKD', str(file_.name)).encode('ascii', 'ignore').lower()

        #remove espaçamentos extras e substitui " " por "_"#
        nome_arquivo = re.sub(r'\s+', ' ', nome_arquivo.decode()).replace(' ','_')

        #nome e extensão#
        arquivo, extensao = os.path.splitext(nome_arquivo)

        #remove caracters não alfanumericos do nome do arquivo#
        arquivo = ''.join(
                [c for c in arquivo if c.isalpha() or c.isdigit() or c=='_']
                ).rstrip()

        #novo nome do arquivo#
        novo_nome = '{0}{1}'.format(arquivo, extensao)

        file_path = default_storage.save(
                os.path.join(upload_to or UPLOAD_PATH, novo_nome), file_)

        url = os.path.join(settings.MEDIA_URL, file_path)

        #registrar thumbs para fields ajaximage#
        upload_thumb = {'fotos': 'admin_imovel_fieldsets',
                        'slides': 'admin_slides_thumb'}

        return HttpResponse(json.dumps(
                    {'url': static(get_thumbnailer(url)[upload_thumb[upload_to]].url),
                     'filename': file_path}))

    return HttpResponse(status=403)
