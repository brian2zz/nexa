import ProductList from '@/pages/ProductList.vue';
import ProductForm from '@/pages/ProductForm.vue';

export default [
  {
    path: '/products',
    name: '{{ model_name.lower() }}_list',
    component: ProductList,
    meta: { title: 'Product List' }
  },
  {
    path: '/products/create',
    name: '{{ model_name.lower() }}_create',
    component: ProductForm,
    meta: { title: 'Create Product' }
  },
  {
    path: '/products/:id/edit',
    name: '{{ model_name.lower() }}_edit',
    component: ProductForm,
    meta: { title: 'Edit Product' }
  }
];
