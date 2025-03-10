import pandas as pd
import numpy as np
from gensim.models import Word2Vec
from nltk.tokenize import word_tokenize
import nltk
from sklearn.preprocessing import MinMaxScaler, StandardScaler

target_columns = ['manufacturer_name', 'model_name', 'year_produced', 'transmission', 'color', 
                  'odometer_value', 'price_usd', 'previous_owners', 'engine_type', 'body_type']
other_features = ['transmission', 'color', 'previous_owners', 'engine_type', 'body_type']
numerical_features = ['odometer_value', 'price_usd', 'year_produced']
w2v_models_path = 'data/models'

nltk.download('punkt_tab')

def preprocess_data(sold_cars_db, cars_for_sale_db):

    # Преобразуем данные в DataFrame для анализа
    saled_cars = pd.DataFrame([{
        'id': car.id,
        'manufacturer_name': car.manufacturer_name,
        'model_name': car.model_name,
        'transmission': car.transmission,
        'year_produced': car.year_produced,
        'odometer_value': car.odometer_value,
        'price_usd': car.price_usd,
        'engine_type': car.engine_type,
        'body_type': car.body_type,
        'color': car.color,
        'previous_owners': car.previous_owners
    } for car in sold_cars_db])

    cars_for_sale = pd.DataFrame([{
        'id': car.id,
        'manufacturer_name': car.manufacturer_name,
        'model_name': car.model_name,
        'transmission': car.transmission,
        'year_produced': car.year_produced,
        'odometer_value': car.odometer_value,
        'price_usd': car.price_usd,
        'engine_type': car.engine_type,
        'body_type': car.body_type,
        'color': car.color,
        'previous_owners': car.previous_owners
    } for car in cars_for_sale_db])

    # Объединяем марку и модель в одну строку
    cars_for_sale['full_car_name'] = cars_for_sale['manufacturer_name'] + ' ' + cars_for_sale['model_name']

    cars_for_sale['full_car_name_cased'] = cars_for_sale['full_car_name'].apply(lambda x: word_tokenize(x.lower()))

    for feature in other_features:
        cars_for_sale[f'{feature}_cased'] = cars_for_sale[feature].apply(lambda x: word_tokenize(x.lower()))

    # Объединяем марку и модель в одну строку
    saled_cars['full_car_name'] = saled_cars['manufacturer_name'] + ' ' + saled_cars['model_name']

    saled_cars['full_car_name_cased'] = saled_cars['full_car_name'].apply(lambda x: word_tokenize(x.lower()))

    for feature in other_features:
        saled_cars[f'{feature}_cased'] = saled_cars[feature].apply(lambda x: word_tokenize(x.lower()))

    # names = pd.concat([cars_for_sale['full_car_name_cased'],saled_cars['full_car_name_cased']]).drop_duplicates()
    # transmissions = pd.concat([cars_for_sale['transmission_cased'],saled_cars['transmission_cased']]).drop_duplicates()
    # colors = pd.concat([cars_for_sale['color_cased'],saled_cars['color_cased']]).drop_duplicates()
    # previous_owners = pd.concat([cars_for_sale['previous_owners_cased'],saled_cars['previous_owners_cased']]).drop_duplicates()
    # engine_types = pd.concat([cars_for_sale['engine_type_cased'],saled_cars['engine_type_cased']]).drop_duplicates()
    # body_types = pd.concat([cars_for_sale['body_type_cased'],saled_cars['body_type_cased']]).drop_duplicates()

    # Обучаем модель Word2Vec
    # w2v_names = Word2Vec(sentences=names, vector_size=30, window=5, min_count=1, sg=0)
    # w2v_transmissions = Word2Vec(sentences=transmissions, vector_size=2, window=5, min_count=1, sg=0)
    # w2v_colors = Word2Vec(sentences=colors, vector_size=20, window=15, min_count=1, sg=0)
    # w2v_previous_owners = Word2Vec(sentences=previous_owners, vector_size=4, window=5, min_count=1, sg=0)
    # w2v_engine_types = Word2Vec(sentences=engine_types, vector_size=2, window=5, min_count=1, sg=0)
    # w2v_body_types = Word2Vec(sentences=body_types, vector_size=15, window=5, min_count=1, sg=0)

    # Загрузка моделей из файлов
    w2v_names = Word2Vec.load(w2v_models_path + "/w2v_names.model")
    w2v_transmissions = Word2Vec.load(w2v_models_path + "/w2v_transmissions.model")
    w2v_colors = Word2Vec.load(w2v_models_path + "/w2v_colors.model")
    w2v_previous_owners = Word2Vec.load(w2v_models_path + "/w2v_previous_owners.model")
    w2v_engine_types = Word2Vec.load(w2v_models_path + "/w2v_engine_types.model")
    w2v_body_types = Word2Vec.load(w2v_models_path + "/w2v_body_types.model")

    # Функция для получения эмбеддинга
    def get_w2v_embedding(model, tokens, vector_size=100):
        embeddings = np.array([model.wv[word] for word in tokens if word in model.wv])
        if embeddings.size == 0:  # Проверяем, пуст ли массив
            return np.zeros(vector_size)
        return np.sum(embeddings, axis=0)

    # Получаем эмбеддинги для каждого автомобиля
    cars_for_sale["full_car_name_embedding"] = cars_for_sale['full_car_name_cased'].apply(lambda x: get_w2v_embedding(w2v_names, x))
    cars_for_sale["transmission_embedding"] = cars_for_sale['transmission_cased'].apply(lambda x: get_w2v_embedding(w2v_transmissions, x))
    cars_for_sale["colors_embedding"] = cars_for_sale['color_cased'].apply(lambda x: get_w2v_embedding(w2v_colors, x))
    cars_for_sale["previous_owners_embedding"] = cars_for_sale['previous_owners_cased'].apply(lambda x: get_w2v_embedding(w2v_previous_owners, x))
    cars_for_sale["engine_type_embedding"] = cars_for_sale['engine_type_cased'].apply(lambda x: get_w2v_embedding(w2v_engine_types, x))
    cars_for_sale["body_type_embedding"] = cars_for_sale['body_type_cased'].apply(lambda x: get_w2v_embedding(w2v_body_types, x))

    saled_cars["full_car_name_embedding"] = saled_cars['full_car_name_cased'].apply(lambda x: get_w2v_embedding(w2v_names, x))
    saled_cars["transmission_embedding"] = saled_cars['transmission_cased'].apply(lambda x: get_w2v_embedding(w2v_transmissions, x))
    saled_cars["colors_embedding"] = saled_cars['color_cased'].apply(lambda x: get_w2v_embedding(w2v_colors, x))
    saled_cars["previous_owners_embedding"] = saled_cars['previous_owners_cased'].apply(lambda x: get_w2v_embedding(w2v_previous_owners, x))
    saled_cars["engine_type_embedding"] = saled_cars['engine_type_cased'].apply(lambda x: get_w2v_embedding(w2v_engine_types, x))
    saled_cars["body_type_embedding"] = saled_cars['body_type_cased'].apply(lambda x: get_w2v_embedding(w2v_body_types, x))

    # Нормализация числовых признаков с помощью MinMaxScaler
    scaler = StandardScaler()
    scaler_mm = MinMaxScaler()
    cars_for_sale[['odometer_value_scaled_mm', 'price_usd_scaled_mm', 'year_produced_scaled_mm']] = scaler_mm.fit_transform(cars_for_sale[numerical_features])
    saled_cars[['odometer_value_scaled_mm', 'price_usd_scaled_mm', 'year_produced_scaled_mm']] = scaler_mm.fit_transform(saled_cars[numerical_features])

    cars_for_sale[['odometer_value_scaled', 'price_usd_scaled', 'year_produced_scaled']] = scaler.fit_transform(cars_for_sale[numerical_features])
    saled_cars[['odometer_value_scaled', 'price_usd_scaled', 'year_produced_scaled']] = scaler.fit_transform(saled_cars[numerical_features])

    cars_for_sale['full_vector'] = cars_for_sale.apply(
        lambda x: np.concatenate([
            x['full_car_name_embedding'],
            x['transmission_embedding'],
            x['colors_embedding'],
            x['previous_owners_embedding'],
            x['engine_type_embedding'],
            x['body_type_embedding'],
            np.array([x['price_usd_scaled_mm']]),  # Преобразуем число в одномерный массив
            np.array([x['odometer_value_scaled_mm']]),  # Преобразуем число в одномерный массив
            np.array([x['year_produced_scaled_mm']]),
        ]), axis=1
    )

    saled_cars['full_vector'] = saled_cars.apply(
        lambda x: np.concatenate([
            x['full_car_name_embedding'],
            x['transmission_embedding'],
            x['colors_embedding'],
            x['previous_owners_embedding'],
            x['engine_type_embedding'],
            x['body_type_embedding'],
            np.array([x['price_usd_scaled_mm']]),  # Преобразуем число в одномерный массив
            np.array([x['odometer_value_scaled_mm']]),  # Преобразуем число в одномерный массив
            np.array([x['year_produced_scaled_mm']]),
        ]), axis=1
    )

    cars_for_sale['full_vector_for_reg'] = cars_for_sale.apply(
        lambda x: np.concatenate([
            x['full_car_name_embedding'],
            x['transmission_embedding'],
            x['colors_embedding'],
            x['previous_owners_embedding'],
            x['engine_type_embedding'],
            x['body_type_embedding'],
            np.array([x['price_usd_scaled']]),  # Преобразуем число в одномерный массив
            np.array([x['odometer_value_scaled']]),  # Преобразуем число в одномерный массив
            np.array([x['year_produced_scaled']]),
        ]), axis=1
    )

    saled_cars['full_vector_for_reg'] = saled_cars.apply(
        lambda x: np.concatenate([
            x['full_car_name_embedding'],
            x['transmission_embedding'],
            x['colors_embedding'],
            x['previous_owners_embedding'],
            x['engine_type_embedding'],
            x['body_type_embedding'],
            np.array([x['price_usd_scaled']]),  # Преобразуем число в одномерный массив
            np.array([x['odometer_value_scaled']]),  # Преобразуем число в одномерный массив
            np.array([x['year_produced_scaled']]),
        ]), axis=1
    )
    
    # Предобработка и возвращаем DataFrame
    return saled_cars, cars_for_sale
