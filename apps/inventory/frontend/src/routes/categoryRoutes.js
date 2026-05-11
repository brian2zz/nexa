import CategoryList from '@/pages/CategoryList.vue';
import CategoryForm from '@/pages/CategoryForm.vue';

export default [
  {
    path: '/categories',
    name: '{{ model_name.lower() }}_list',
    component: CategoryList,
    meta: { title: 'Category List' }
  },
  {
    path: '/categories/create',
    name: '{{ model_name.lower() }}_create',
    component: CategoryForm,
    meta: { title: 'Create Category' }
  },
  {
    path: '/categories/:id/edit',
    name: '{{ model_name.lower() }}_edit',
    component: CategoryForm,
    meta: { title: 'Edit Category' }
  }
];
