import axios from 'axios'

const csrf = document
  .querySelector('meta[name="csrf-token"]')
  ?.getAttribute('content')

const http = axios.create({

  headers: {
    'X-CSRFToken': csrf
  }

})

export default http