"""Contains the LiteCollection class"""
from pylite.lite_exceptions import ModelInstanceNotFoundError, DuplicateModelInstance


class LiteCollection:
    """A collection of LiteModel instances"""

    # Class-level attribute to store the table name
    table = None

    def __init__(self, model_instances=None):
        self.list = []
        if model_instances:
            for instance in model_instances:
                self.add(instance)

    def __str__(self) -> str:
        return [model_instance.to_dict() for model_instance in self.list].__str__()

    def __repr__(self) -> str:
        return str(self.list)

    def __add__(self, other) -> "LiteCollection":
        self_list = self.list[:]

        def add_model(model):
            if model not in self_list and self._model_is_consistent(model):
                self_list.append(model)

        if isinstance(other, LiteCollection):
            for model in other.list:
                add_model(model)
        elif isinstance(other, list):
            for model in other:
                add_model(model)
        else:
            base_classes = [b_c.__name__ for b_c in other.__class__.__bases__]
            if "LiteModel" in base_classes and other not in self_list:
                self_list.append(other)
            else:
                raise DuplicateModelInstance(other)

        return LiteCollection(self_list)

    def __len__(self) -> int:
        return len(self.list)

    def __eq__(self, other) -> bool:
        if other.__class__.__name__ == "LiteCollection":
            return self.list == other.list
        return self.list == other

    def __contains__(self, item) -> bool:
        """Used by 'in' Python comparison.

        Args:
            item (LiteModel, int): if an integer, looks for a model with the given primary key.
        """

        # If an integer
        if isinstance(item, int):
            return any(getattr(model, "id") == item for model in self.list)

        # If a LiteModel
        return item in self.list

    def __getitem__(self, item) -> "LiteModel":
        return self.list[item]

    def _model_is_consistent(self, model_instance) -> bool:
        """Checks if the model instance is the same type as
        the existing models in the collection."""

        # Check if table name matches existing models
        if (
            self.table is not None
            and model_instance.table.table_name != self.table.table_name
        ):
            raise TypeError(
                "Model instance is not of the same type as existing models in this collection."
            )

        return True

    def add(self, model_instance) -> None:
        """Adds a LiteModel instance to the collection.

        Args:
            model_instance (LiteModel): LiteModel instance

        Raises:
            DuplicateModelInstance: Model instance already exists in LiteCollection.
            WrongModelType: Model instance is not of the same type as existing models in the collection.
        """

        # Check if LiteModel instance is already in this collection
        if model_instance in self.list:
            raise DuplicateModelInstance(model_instance)

        # Check if model is consistent with the collection
        if self._model_is_consistent(model_instance):
            self.list.append(model_instance)

        # Set the table name if it hasn't been set already
        if not self.table:
            self.table = model_instance.table

    def attach_many_to_all(self, model_instances) -> None:
        """Attaches a list of model instances to the all model instances in the collection.

        Args:
            model_instances (list): List of LiteModel instances

        Raises:
            RelationshipError: Relationship already exists.
        """

        for model in self.list:
            model.attach_many(model_instances)

    def detach_many_from_all(self, model_instances) -> None:
        """Detaches a list of model instances from all the model instances in the collection.

        Args:
            model_instances (list): List of LiteModel instances.
            self_fkey (str, optional): Foreign key to use for the self-model. Defaults to None.
            model_fkey (str, optional):
                Foreign key to use for the model being detached. Defaults to None.

        Raises:
            RelationshipError: Relationship does not exist.
        """

        for model in self.list:
            model.detach_many(model_instances)

    def attach_to_all(
        self, model_instance, self_fkey: str = None, model_fkey: str = None
    ) -> None:
        """Attaches a model instance to the all model instances in the collection.

        Args:
            model_instance (LiteModel): LiteModel instance

        Raises:
            RelationshipError: Relationship already exists.
        """

        for model in self.list:
            model.attach(model_instance, self_fkey, model_fkey)

    def detach_from_all(self, model_instance) -> None:
        """
        Detaches a given model instance from all the model instances in the collection.

        Args:
            model_instance (LiteModel): The model instance to detach from all the model instances.
            self_fkey (str): The foreign key in this model instance
                that points to the other model instance (default is None).
            model_fkey (str): The foreign key in the other model instance
                that points to this model instance (default is None).
        """

        for model in self.list:
            model.detach(model_instance)

    def first(self) -> "LiteModel":
        """Returns the first model instance in the collection."""

        return self.list[0]

    def last(self) -> "LiteModel":
        """Returns the last model instance in the collection."""

        return self.list[-1]

    def sort(self, field: str = "id", reverse: bool = False) -> "LiteCollection":
        """Sorts the collection by the given field. Defaults to model's id.

        Args:
            field (str): Field to order by
            reverse (bool, optional): Whether to reverse the order. Defaults to False.
        """

        self.list.sort(key=lambda x: getattr(x, field), reverse=reverse)
        return self

    def fresh(self) -> None:
        """Retrieves a fresh copy of each model instance in the collection from the database."""

        for model in self.list:
            model.fresh()

    def delete_all(self) -> None:
        """Deletes all model instances in the collection from the database."""

        for model in self.list:
            model.delete()

    def model_keys(self) -> list:
        """Returns a list of primary keys for models in the collection."""

        return [model.id for model in self.list]

    def join(self, lite_collection) -> "LiteCollection":
        """Returns the union of two collections.

        Args:
            lite_collection (LiteCollection): LiteCollection instance
        """

        return LiteCollection(self.list + lite_collection.list)

    def intersection(self, lite_collection) -> "LiteCollection":
        """Returns the intersection of two collections.

        Args:
            lite_collection (LiteCollection): LiteCollection instance

        Returns:
            LiteCollection: Collection of LiteModel instances forming intersection
        """

        self_keys = set(self.model_keys())
        other_keys = set(lite_collection.model_keys())

        intersection_keys = list(self_keys.intersection(other_keys))

        return LiteCollection(
            [model for model in self.list if model.id in intersection_keys]
        )

    def difference(self, lite_collection) -> "LiteCollection":
        """Returns all models not in the passed collection.

        Args:
            lite_collection (LiteCollection): LiteCollection instance

        Returns:
            LiteCollection: Collection of LiteModel instances forming intersection
        """

        difference_keys = set(self.model_keys()) - set(lite_collection.model_keys())
        return LiteCollection(
            [model for model in self.list if model.id in difference_keys]
        )

    def remove(self, model_instance) -> None:
        """Removes a LiteModel instance from this collection.

        Args:
            model_instance (LiteModel): LiteModel instance to remove

        Raises:
            ModelInstanceNotFoundError: LiteModel instance does not exist in this collection.
        """

        try:
            self.list.remove(model_instance)
        except ValueError as exc:
            raise ModelInstanceNotFoundError(model_instance.id) from exc

    def where(self, column_name) -> "LiteCollection":
        """Simulates a select query on this collection.

        Args:
            where_columns (list): [
                [column_name, ('=','<','>','LIKE'), column_value]
            ]

        Returns:
            LiteCollection: Matching LiteModel instances
        """

        # Collect ids of models inside collection
        ids = [model.id for model in self.list]

        # Return a new LiteCollection with the matching models
        return self.list[0].where("id").is_in(ids).and_where(column_name)
