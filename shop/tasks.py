from shop import models
from ecommerce.celery import app

from PIL import Image


@app.task(name='save_company_image')
def save_company_image(pk):
    company = models.Company.objects.get(pk=pk)
    imag = Image.open(company.logo.path)
    output_size = (200, 200)
    imag.thumbnail(output_size)
    imag.save(company.logo.path)


@app.task(name='save_subcategory_image')
def save_subcategory_image(pk):
    subcategory = models.SubCategory.objects.get(pk=pk)
    imag = Image.open(subcategory.image.path)
    output_size = (200, 200)
    imag.thumbnail(output_size)
    imag.save(subcategory.image.path)


@app.task(name='save_category_image')
def save_category_image(pk):
    category = models.Category.objects.get(pk=pk)
    imag = Image.open(category.image.path)
    output_size = (200, 200)
    imag.thumbnail(output_size)
    imag.save(category.image.path)


@app.task(name='save_item_image')
def save_item_image(pk):
    item = models.Item.objects.get(pk=pk)
    imag = Image.open(item.image.path)
    output_size = (200, 200)
    imag.thumbnail(output_size)
    imag.save(item.image.path)
