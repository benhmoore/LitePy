from colorama import Fore, Back, Style

import os
from lite import *

class LiteCollection:
    """Container for LiteModel instances. Provides useful methods and overloads for common operations."""

    def __init__(self, model_instances:list=None):
        """Initializes new LiteCollection with given list of LiteModel instances.

        Args:
            model_instances (list, optional): List of LiteModel instances. Defaults to None.
        """        
        self.list = []
        if model_instances: 
            for instance in model_instances:
                if instance not in self.list: self.list.append(instance)


    def __str__(self):
        print_list = []
        for model_instance in self.list:
            print_list.append(model_instance._toDict())
        return print_list.__str__()


    def __len__(self):
        return len(self.list)


    def __eq__(self, other):
        if other.__class__.__name__ == 'LiteCollection':
            if self.list == other.list:
                return True
            else:
                return False
        elif other.__class__.__name__ == 'list':
            if self.list == other:
                return True
            else:
                return False


    def __contains__(self, item):
        """Used by 'in' Python comparison.

        Args:
            item (LiteModel, int): if an integer, looks for a model with the given primary key.
        """

        # If an integer
        if type(item) is int:
            for model in self.list:
                if getattr(model,'id') == item:
                    return True
            return False

        # If a LiteModel
        if item in self.list:
            return True
        else:
            return False


    def __getitem__(self, item): return self.list[item]


    def add(self, model_instance):
        """Adds a LiteModel instance to the collection.

        Args:
            model_instance (LiteModel): LiteModel instance

        Raises:
            DuplicateModelInstance: Model instance already exists in LiteCollection
        """

        # Check if LiteModel instance is already in this collection
        if model_instance in self.list: raise DuplicateModelInstance(model_instance)

        self.list.append(model_instance)


    def fresh(self):
        """Retrieves a fresh copy of each model instance in the collection from the database."""

        for model in self.list: model.fresh()

    
    def modelKeys(self) -> list:
        """Returns a list of primary keys for models in the collection."""

        return [model.id for model in self.list]


    def join(self, lite_collection):
        """Merges two LiteCollection instances.

        Args:
            lite_collection (LiteCollection): LiteCollection instance
        """
        
        self.list += lite_collection.list


    def intersection(self, lite_collection):
        """Returns the intersection of two collections.

        Args:
            lite_collection (LiteCollection): LiteCollection instance

        Returns:
            LiteCollection: Collection of LiteModel instances forming intersection
        """

        self_keys = set(self.modelKeys())
        other_keys = set(lite_collection.modelKeys())

        intersection_keys = list(self_keys.intersection(other_keys))

        intersection = LiteCollection()
        for model in self.list:
            if model.id in intersection_keys:
                intersection.add(model)
        
        return intersection

    
    def difference(self, lite_collection):
        """Returns all models not in the passed collection.

        Args:
            lite_collection (LiteCollection): LiteCollection instance

        Returns:
            LiteCollection: Collection of LiteModel instances forming intersection
        """

        difference = LiteCollection()
        for model in self.list:
            if model not in lite_collection:
                difference.add(model)
        
        return difference


    def remove(self, model_instance):
        """Removes a LiteModel instance from this collection.

        Args:
            model_instance (LiteModel): LiteModel instance to remove

        Raises:
            ModelInstanceNotFoundError: LiteModel instance does not exist in this collection.
        """

        try: self.list.remove(model_instance)
        except: raise ModelInstanceNotFoundError(model_instance.id)


    def where(self, where_columns:list):
        """Simulates a select query on this collection.

        Args:
            where_columns (list): [
                [column_name, ('=','<','>','LIKE'), column_value]
            ]

        Returns:
            LiteCollection: Matching LiteModel instances
        """

        results_collection = []
        for model in self.list:
            should_add = True
            for condition in where_columns:
                if condition[1] == '=':
                    if getattr(model,condition[0]) != condition[2]:
                        should_add = False
                elif condition[1] == '!=':
                    if getattr(model,condition[0]) == condition[2]:
                        should_add = False
                        
                elif condition[1] == 'LIKE':
                    if condition[2][1:-1] not in getattr(model,condition[0]): # clipped string removes SQL's '%' from beginning and end
                        should_add = False
                elif condition[1] == 'NOT LIKE':
                    if condition[2][1:-1] in getattr(model,condition[0]): # clipped string removes SQL's '%' from beginning and end
                        should_add = False
                
                elif condition[1] == '<':
                    if condition[2] <= getattr(model,condition[0]): # clipped string removes SQL's '%' from beginning and end
                        should_add = False
                elif condition[1] == '<=':
                    if condition[2] < getattr(model,condition[0]): # clipped string removes SQL's '%' from beginning and end
                        should_add = False
                
                elif condition[1] == '>':
                    if condition[2] >= getattr(model,condition[0]): # clipped string removes SQL's '%' from beginning and end
                        should_add = False
                elif condition[1] == '>=':
                    if condition[2] > getattr(model,condition[0]): # clipped string removes SQL's '%' from beginning and end
                        should_add = False
            
            if should_add: results_collection.append(model)

        return LiteCollection(results_collection)