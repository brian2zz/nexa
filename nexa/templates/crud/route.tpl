import {{ class_name }}List from '@/pages/{{ class_name }}List.vue';
import {{ class_name }}Form from '@/pages/{{ class_name }}Form.vue';

export default [
  {
    path: '/{{ route_path }}',
    name: '{{ model_name.lower() }}_list',
    component: {{ class_name }}List,
    meta: { title: '{{ class_name }} List' }
  },
  {
    path: '/{{ route_path }}/create',
    name: '{{ model_name.lower() }}_create',
    component: {{ class_name }}Form,
    meta: { title: 'Create {{ class_name }}' }
  },
  {
    path: '/{{ route_path }}/:id/edit',
    name: '{{ model_name.lower() }}_edit',
    component: {{ class_name }}Form,
    meta: { title: 'Edit {{ class_name }}' }
  }
];
