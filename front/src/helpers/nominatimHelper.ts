import ky from 'ky';

const nominatimUrl = 'http://localhost:5173/nominatim';

// countries in which nominatim searches
const countryCodesArray = ['fr', 'be'];

// the language nominatim returns for the places names
const accept_language = ['fr'];

const nominatimRequest = async (url: string, params: Record<string, any>) => {
    // the output format
    params.format = 'json';

    if (params.countryCodesArray) {
        params.countrycodes = params.countryCodesArray.join(',');
    }

    if (params.accept_language) {
        params['accept-language'] = params.accept_language;
    }

    const searchParams = new URLSearchParams(params as Record<string, string>);
    const fullUrl = `${url}?${searchParams.toString()}`;

    console.log(fullUrl);

    try {
        const res = await ky.get(fullUrl).json<any>();
        return res;
    } catch (error) {
        console.log('Nominatim error: ' + error);
        return undefined;
    }
};

/**
 * Get the GPS coordinates of a place
 * @param searchString The place to look for (state, city, road...)
 * @returns The data of the response
 */
const nominatimSearch = async (searchString: string) => {
    const params = {
        q: searchString,
        countryCodesArray: countryCodesArray,
        accept_language: accept_language,
    };

    const url = `${nominatimUrl}/search`;

    return nominatimRequest(url, params);
};

/**
 * Get the name of the GPS coordinates (country, state, city, road...)
 * @param lat The latitude
 * @param lon The longitude
 * @returns The data of the response
 */
const nominatimReverse = async (lat: number, lon: number) => {
    const params = {
        lat: lat,
        lon: lon,
        countryCodesArray: countryCodesArray,
        accept_language: accept_language,
    };

    const url = `${nominatimUrl}/reverse`;

    return nominatimRequest(url, params);
};

/**
 *
 * @param lat The latitude
 * @param lon The longitude
 * @returns The formatted address of the GPS coordinates: road, city
 */
const nominatimReverseWrittenAddress = async (lat: number, lon: number) => {
    let location = '';
    const result = await nominatimReverse(lat, lon).catch((error) => {
        console.log(error);
    });

    if (result == null) {
        return 'Address not found';
    }

    if (result.address.road != undefined) {
        location = result.address.road + ', ';
    }

    if (result.address.city != undefined) {
        location += result.address.city;
    } else {
        location += result.address.municipality;
    }

    return location;
};

export default {
    nominatimSearch,
    nominatimReverse,
    nominatimReverseWrittenAddress,
};
