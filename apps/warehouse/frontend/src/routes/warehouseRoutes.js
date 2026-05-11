import WarehouseList from '@/pages/WarehouseList.vue';
import WarehouseForm from '@/pages/WarehouseForm.vue';

export default [
  {
    path: '/warehouses',
    name: '{{ model_name.lower() }}_list',
    component: WarehouseList,
    meta: { title: 'Warehouse List' }
  },
  {
    path: '/warehouses/create',
    name: '{{ model_name.lower() }}_create',
    component: WarehouseForm,
    meta: { title: 'Create Warehouse' }
  },
  {
    path: '/warehouses/:id/edit',
    name: '{{ model_name.lower() }}_edit',
    component: WarehouseForm,
    meta: { title: 'Edit Warehouse' }
  }
];
