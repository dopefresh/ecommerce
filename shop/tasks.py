from shop import models
from ecommerce.celery import app

from PIL import Image
from loguru import logger


@logger.catch
@app.task(name='save_company_image')
def save_company_image(pk):
    logger.info('Task save company image called')
    company = models.Company.objects.get(pk=pk)
    imag = Image.open(company.logo.path)
    output_size = (200, 200)
    imag.thumbnail(output_size)
    imag.save(company.logo.path)


@logger.catch
@app.task(name='save_subcategory_image')
def save_subcategory_image(pk):
    logger.info('Task save subcategory image called')
    subcategory = models.Subcategory.objects.get(pk=pk)
    imag = Image.open(subcategory.image.path)
    output_size = (200, 200)
    imag.thumbnail(output_size)
    imag.save(subcategory.image.path)


@logger.catch
@app.task(name='save_category_image')
def save_category_image(pk):
    logger.info('Task save category image called')
    category = models.Category.objects.get(pk=pk)
    imag = Image.open(category.image.path)
    output_size = (200, 200)
    imag.thumbnail(output_size)
    imag.save(category.image.path)


@logger.catch
@app.task(name='save_item_image')
def save_item_image(pk):
    logger.info('Task save item image called')
    item = models.Item.objects.get(pk=pk)
    imag = Image.open(item.image.path)
    output_size = (200, 200)
    imag.thumbnail(output_size)
    imag.save(item.image.path)
