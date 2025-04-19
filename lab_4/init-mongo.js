db = db.getSiblingDB('products_db');
db.createCollection('products');

const categories = [
  "Electronics", "Computers", "Smart Home", "Audio", "Photography", 
  "Wearables", "Gaming", "Kitchen Appliances", "Home Appliances", 
  "Office Equipment", "Smartphones", "Tablets", "Accessories", 
  "Networking", "Storage", "Software", "Security", "TV & Video", 
  "Outdoor Tech", "Toys & Gadgets"
];

const adjectivesPart1 = [
  "Advanced", "Smart", "Ultra", "Premium", "Professional", "Digital", 
  "Wireless", "Portable", "High-End", "Compact", "Sleek", "Classic", 
  "Modern", "Innovative", "Ergonomic", "Lightweight", "Rugged", "Elite", 
  "Performance", "Eco-Friendly"
];

const adjectivesPart2 = [
  "Pro", "Max", "Elite", "Ultimate", "Plus", "X", "Lite", "Mini", "Mega", 
  "Turbo", "Extreme", "Prime", "Expert", "Deluxe", "Basic", "Standard", 
  "Enhanced", "Special", "Limited", "Essential"
];

const productTypes = [
  "Laptop", "Smartphone", "Tablet", "Headphones", "Speaker", "Camera", 
  "Monitor", "Keyboard", "Mouse", "Router", "Drone", "Watch", "TV", 
  "Printer", "Scanner", "Console", "Controller", "Charger", "Hub", "Drive"
];

function getRandomInt(min, max) {
  return Math.floor(Math.random() * (max - min + 1)) + min;
}

function getRandomPrice(min, max) {
  return (Math.random() * (max - min) + min).toFixed(2);
}

function generateProductName() {
  const adj1 = adjectivesPart1[getRandomInt(0, adjectivesPart1.length - 1)];
  const adj2 = adjectivesPart2[getRandomInt(0, adjectivesPart2.length - 1)];
  const type = productTypes[getRandomInt(0, productTypes.length - 1)];
  const model = getRandomInt(100, 9999);

  const formats = [
    `${adj1} ${type} ${adj2} ${model}`,
    `${adj1} ${type} ${model}`,
    `${type} ${adj2} ${model}`,
    `${adj1} ${adj2} ${type}`,
    `${type} ${model} ${adj2}`
  ];
  
  return formats[getRandomInt(0, formats.length - 1)];
}

function generateDescription(name) {
  const featuresPart1 = [
    "features the latest technology", 
    "comes with cutting-edge features", 
    "designed for optimal performance", 
    "built with premium materials", 
    "engineered to exceed expectations",
    "perfectly balanced for daily use",
    "incorporates next-gen innovation",
    "sets a new standard in its category"
  ];
  
  const featuresPart2 = [
    "ensuring a seamless experience", 
    "providing exceptional value", 
    "delivering outstanding results", 
    "perfect for both work and play", 
    "ideal for professionals and enthusiasts",
    "suitable for all skill levels",
    "adaptable to various environments",
    "satisfying even the most demanding users"
  ];
  
  const part1 = featuresPart1[getRandomInt(0, featuresPart1.length - 1)];
  const part2 = featuresPart2[getRandomInt(0, featuresPart2.length - 1)];
  
  return `The ${name} ${part1}, ${part2}. This product represents the perfect balance of quality, performance, and affordability.`;
}

let products = [];

const PRODUCT_COUNT = 10000;

for (let i = 1; i <= PRODUCT_COUNT; i++) {
  const name = generateProductName();
  const category = categories[getRandomInt(0, categories.length - 1)];
  const price = getRandomPrice(9.99, 2999.99);
  const inStock = getRandomInt(0, 100);
  
  products.push({
    name: name,
    description: generateDescription(name),
    price: parseFloat(price),
    category: category,
    in_stock: inStock
  });

  if (i % 1000 === 0 || i === PRODUCT_COUNT) {
    db.products.insertMany(products);
    products = [];
  }
}

db.products.createIndex({ name: 1 });
db.products.createIndex({ category: 1 });
db.products.createIndex({ price: 1 });

print(`MongoDB initialization completed: ${PRODUCT_COUNT} products inserted`);
