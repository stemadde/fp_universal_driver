import inspect


def validate(class_instance: object) -> None:
    """
    Lookup for all the __validate* methods in the class_instance and run them
    :raise Assertion Error if any of the validations fail
    """
    # Build a validators var that contains the validator functions for each attribute
    validators = []
    methods = inspect.getmembers(class_instance, predicate=inspect.ismethod)
    for method in [m for m in methods if (m[0].startswith('__validate') and not m[0].endswith('validate__'))]:
        assert hasattr(class_instance, method[0]), f'Your class {class_instance} does not have a {method[0]} validator'
        validators.append(getattr(class_instance, method[0]))

    # Run the validations
    for validator in validators:
        validator()


def is_equal(object1, object2) -> bool:
    if not isinstance(object1, type(object2)):
        return False
    attributes = inspect.getmembers(object1, lambda a: not (inspect.isroutine(a)))
    attributes = [a for a in attributes if not (a[0].startswith('__') and a[0].endswith('__'))]
    for attribute in attributes:
        if attribute[1] != getattr(object2, attribute[0]):
            return False
    return True
