#!/usr/bin/python
# -*- coding:utf-8 -*-


def standardize_instance(unstandardized_instance, aim_class,  name_id_dict):
    try:
        if isinstance(unstandardized_instance, aim_class):
            return unstandardized_instance.id
        elif isinstance(unstandardized_instance, int):
            return unstandardized_instance
        elif name_id_dict and isinstance(unstandardized_instance, str):
            return name_id_dict[unstandardized_instance]
        else:
            raise AttributeError
    except Exception, e:
        print Exception, e
        print 'the role ' + unstandardized_instance + ' does not exist actually.'


class ManyToMany(object):
    def __init__(self, db, classb, class_relation, relation_attribute_a, relation_attribute_b):
        self.db = db
        self.classb = classb
        self.class_relation = class_relation
        self.relation_attribute_a = relation_attribute_a
        self.relation_attribute_b = relation_attribute_b

    def __get__(self, obj, type):
        if not obj.id:
            return []
        relations = self.class_relation.query.filter(eval('self.class_relation.' + self.relation_attribute_a + ' == obj.id')).all()
        classb_ids = [eval('relation.' + self.relation_attribute_b) for relation in relations]
        return self.classb.query.filter(self.classb.id.in_(classb_ids))

    def __set__(self, obj, val):
        if not obj.id:
            return
        self.class_relation.query.filter(eval('self.class_relation.' + self.relation_attribute_a + ' == obj.id')).delete()

        if hasattr(self.classb, 'name'):
            name_id_dict = {b.name: b.id for b in self.classb.query.all()}
        else:
            name_id_dict = None

        b_ids_to_add = val
        if not isinstance(b_ids_to_add, list):
            b_ids_to_add = [b_ids_to_add]

        b_ids_to_add = [standardize_instance(b_id_to_add, self.classb, name_id_dict) for b_id_to_add in b_ids_to_add]
        relations_to_add = [eval('self.class_relation(' + self.relation_attribute_a + '=obj.id, ' + self.relation_attribute_b + '=b_id_to_add)') for b_id_to_add in b_ids_to_add]
        self.db.session.add_all(relations_to_add)

    def __delete__(self, obj):
        if not obj.id:
            return
        self.class_relation.query.filter(eval('self.class_relation.' + self.relation_attribute_a + ' == obj.id')).delete()

    def standardize_role(self, unstandardized_role, name_id_dict):
        try:
            if isinstance(unstandardized_role, self.classb):
                return unstandardized_role.id
            elif isinstance(unstandardized_role, int):
                return unstandardized_role
            elif name_id_dict and isinstance(unstandardized_role, str):
                return name_id_dict[unstandardized_role]
            else:
                raise AttributeError
        except Exception, e:
            print Exception, e
            print 'the role ' + unstandardized_role + ' does not exist actually.'

    def append(self, a_id, b_ids_to_add):
        relations = self.class_relation.query.filter(eval('self.class_relation.' + self.relation_attribute_a + ' == a_id')).all()
        existed_roles_id = [eval('relation.' + self.relation_attribute_b) for relation in relations]

        if hasattr(self.classb, 'name'):
            name_id_dict = {b.name: b.id for b in self.classb.query.all()}
        else:
            name_id_dict = None
        if not isinstance(b_ids_to_add, list):
            b_ids_to_add = [b_ids_to_add]

        b_ids_to_add = [self.standardize_role(b_id_to_add, name_id_dict) for b_id_to_add in b_ids_to_add]
        b_ids_to_add = [b_id_to_add for b_id_to_add in b_ids_to_add if b_id_to_add and b_id_to_add not in existed_roles_id]
        relations_to_add = [eval('self.class_relation(' + self.relation_attribute_a + '=a_id, ' + self.relation_attribute_b + '=b_id_to_add)') for b_id_to_add in b_ids_to_add]
        self.db.session.add_all(relations_to_add)

    def delete(self, a_id, b_ids_to_del):
        relations = self.class_relation.query.filter(eval('self.class_relation.' + self.relation_attribute_a + ' == a_id')).all()
        existed_roles_id = [eval('relation.' + self.relation_attribute_b) for relation in relations]

        name_id_dict = {b.name: b.id for b in self.classb.query.all()}
        if not isinstance(b_ids_to_del, list):
            b_ids_to_del = [b_ids_to_del]

        b_ids_to_del = [self.standardize_role(b_id_to_del, name_id_dict) for b_id_to_del in b_ids_to_del]
        b_ids_to_del = [b_id_to_del for b_id_to_del in b_ids_to_del if b_id_to_del and b_id_to_del in existed_roles_id]
        relations_to_del = self.class_relation.query.filter(eval('self.class_relation.' + self.relation_attribute_a + ' == a_id')).filter(eval('self.class_relation.' + self.relation_attribute_b + '.in_(roles_id_to_del)')).all()
        for relation in relations_to_del:
            self.db.session.delete(relation)
