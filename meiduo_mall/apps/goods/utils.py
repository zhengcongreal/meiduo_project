
def get_breadcrumb(cat3):
    cat2=cat3.parent
    cat1=cat2.parent
    breadcrumb={
        'cat1':cat1.name,
        'cat2':cat2.name,
        'cat3':cat3.name,
    }
    return breadcrumb