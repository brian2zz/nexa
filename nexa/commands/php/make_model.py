import os

def handle(args):
    if len(args) < 2:
        print('Usage: nexa php make:model [module] [model_name]')
        return

    module_name = args[0].lower()
    model_name = args[1]

    # Convert model_name to PascalCase if it's not
    model_name = ''.join(word.capitalize() for word in model_name.split('_'))

    apps_dir = os.path.join(os.getcwd(), 'apps')
    module_dir = os.path.join(apps_dir, module_name)
    models_dir = os.path.join(module_dir, 'Models')

    if not os.path.exists(models_dir):
        print(f"Error: Module '{module_name}' Models directory not found. Please create the module first.")
        return

    model_path = os.path.join(models_dir, f"{model_name}.php")
    if os.path.exists(model_path):
        print(f"Error: Model '{model_name}' already exists in module '{module_name}'.")
        return

    namespace = f"Apps\\{module_name.capitalize()}\\Models"
    table_name = f"{module_name}_{model_name.lower()}s"

    content = f"""<?php

namespace {namespace};

use Doctrine\\ORM\\Mapping\\Entity;
use Doctrine\\ORM\\Mapping\\Table;
use Doctrine\\ORM\\Mapping\\Id;
use Doctrine\\ORM\\Mapping\\Column;
use Doctrine\\ORM\\Mapping\\GeneratedValue;
use Doctrine\\ORM\\Mapping\\HasLifecycleCallbacks;
use Doctrine\\ORM\\Mapping\\PrePersist;
use Doctrine\\ORM\\Mapping\\PreUpdate;
use Nexa\\NexaModel;

#[Entity]
#[Table(name: '{table_name}')]
#[HasLifecycleCallbacks]
class {model_name} extends NexaModel
{{
    #[Id]
    #[Column(type: 'integer')]
    #[GeneratedValue]
    public int $id;

    #[Column(type: 'string', length: 255)]
    public string $name;

    #[Column(type: 'datetime')]
    public \\DateTime $created_at;

    #[Column(type: 'datetime', nullable: true)]
    public ?\\DateTime $updated_at = null;

    #[PrePersist]
    public function onPrePersist(): void
    {{
        $this->created_at = new \\DateTime();
    }}

    #[PreUpdate]
    public function onPreUpdate(): void
    {{
        $this->updated_at = new \\DateTime();
    }}
}}
"""

    with open(model_path, 'w') as f:
        f.write(content)

    print(f"Model '{model_name}' created successfully in apps/{module_name}/Models/")
