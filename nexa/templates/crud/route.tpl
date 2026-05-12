export default [
  {
    path: '/nexa-admin/{{ route_path }}',
    name: '{{ model_name.lower() }}_list',
    component: () => import('../pages/{{ class_name }}List.vue'),
    meta: { title: '{{ class_name }} List' }
  },
  {
    path: '/nexa-admin/{{ route_path }}/create',
    name: '{{ model_name.lower() }}_create',
    component: () => import('../pages/{{ class_name }}Form.vue'),
    meta: { title: 'Create {{ class_name }}' }
  },
  {
    path: '/nexa-admin/{{ route_path }}/:id/edit',
    name: '{{ model_name.lower() }}_edit',
    component: () => import('../pages/{{ class_name }}Form.vue'),
    meta: { title: 'Edit {{ class_name }}' }
  }
];
