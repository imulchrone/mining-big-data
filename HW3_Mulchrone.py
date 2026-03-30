# To run locally:
# python MovieSimilarities100k.py --items=ml-100k/u.item ml-100k/u.data

# To run on a single EMR node:
# python HW3_Mulchrone.py -r emr --items=ml-1m/movies.dat ml-1m/ratings.dat --conf-path mrjob.conf > output.txt

# To run on 4 EMR nodes (master node created by default):
# python HW3_Mulchrone.py -r emr --num-core-instances=3 --items=ml-1m/movies.dat ml-1m/ratings.dat --conf-path mrjob.conf > output.txt

# Troubleshooting EMR jobs (subsitute your job ID):
# python -m mrjob.tools.emr.fetch_logs --find-failure j-1NXMMBNEQHAFT

"""
Setting up to run (mac instructions).
*If using windows I'd recommend either running this code into your EC2 instance directly or using Putty and then running the commands.
    Alternatively you can set your environment variables as mentioned in the doc here: https://www3.ntu.edu.sg/home/ehchua/programming/howto/Environment_Variables.html#zz-2.2.
    You should be able to use the autoconfiguration and wouldn't need to set mrjob.conf, and you also won't need to add ec2_key_pair info for this assignment.
    
Download and unzip the ml-100k data
>wget http://www.grouplens.org/system/files/ml-100k.zip

Install mrjob
> pip install mrjob==0.6.12
*Use conda environments as we did in class. There's instructions in the D2L Discussion regarding anaconda as well.

Run aws configure
- Install AWS CLI: https://docs.aws.amazon.com/cli/latest/userguide/getting-started-install.html

Run `aws configure in your terminal`
add your credentials for:
    - AWS Access Key ID 
    - AWS Secret Access Key
    - The region should be `us-east-1`
    - output format should be `json`

As we did in class, to get your aws access key, secret access key and session token,
    1. Go to the 'Launch AWS Academy Learner Lab' in AWS academy
    2. click on 'i AWS Details' on the top right.
    3. Click 'Show' next to AWS CLI to get the keys and session token.
All 3 of these should be added to the mrjob.conf file along with the location to your key pairs file.

if needed (you still get an error) edit `~/.aws/credentials` as well to and add your access key and secret key.

Additional info: https://mrjob.readthedocs.io/en/latest/guides/emr-quickstart.html
"""

from mrjob.job import MRJob
from mrjob.step import MRStep
from math import sqrt

from itertools import combinations

class MovieSimilarities(MRJob):

    def configure_args(self):
        super(MovieSimilarities, self).configure_args()
        self.add_file_arg('--items', help='Path to u.item')

    def load_movie_names(self):
        # Load database of movie names.
        self.movieNames = {}

        with open("movies.dat", encoding='ascii', errors='ignore') as f:
            for line in f:
                fields = line.split('::')
                # yield fields, 1
                self.movieNames[int(fields[0])] = fields[1]

    def steps(self):
        return [
            MRStep(mapper=self.mapper_parse_input,
                    reducer=self.reducer_ratings_by_user),
            MRStep(mapper=self.mapper_create_item_pairs,
                    reducer=self.reducer_compute_similarity),
            MRStep(mapper=self.mapper_sort_similarities,
                    mapper_init=self.load_movie_names,
                    reducer=self.reducer_output_similarities)]

    def mapper_parse_input(self, key, line):
        # Outputs userID => (movieID, rating)
        (userID, movieID, rating, timestamp) = line.split('::')
        yield  userID, (movieID, float(rating))

    def reducer_ratings_by_user(self, user_id, itemRatings):
        #Group (item, rating) pairs by userID

        ratings = []
        for movieID, rating in itemRatings:
            ratings.append((movieID, rating))

        yield user_id, ratings

    def mapper_create_item_pairs(self, user_id, itemRatings):
        # Find every pair of movies each user has seen, and emit
        # each pair with its associated ratings

        # "combinations" finds every possible pair from the list of movies
        # this user viewed.
        for itemRating1, itemRating2 in combinations(itemRatings, 2):
            movieID1 = itemRating1[0]
            rating1 = itemRating1[1]
            movieID2 = itemRating2[0]
            rating2 = itemRating2[1]

            # Produce both orders so sims are bi-directional
            yield (movieID1, movieID2), (rating1, rating2)
            yield (movieID2, movieID1), (rating2, rating1)


    def cosine_similarity(self, ratingPairs):
        # Computes the cosine similarity metric between two
        # rating vectors.
        numPairs = 0
        sum_xx = sum_yy = sum_xy = 0
        for ratingX, ratingY in ratingPairs:
            sum_xx += ratingX * ratingX
            sum_yy += ratingY * ratingY
            sum_xy += ratingX * ratingY
            numPairs += 1

        numerator = sum_xy
        denominator = sqrt(sum_xx) * sqrt(sum_yy)

        score = 0
        if (denominator):
            score = (numerator / (float(denominator)))

        return (score, numPairs)

    def reducer_compute_similarity(self, moviePair, ratingPairs):
        # Compute the similarity score between the ratings vectors
        # for each movie pair viewed by multiple people

        # Output movie pair => score, number of co-ratings

        score, numPairs = self.cosine_similarity(ratingPairs)

        # Enforce a minimum score and minimum number of co-ratings
        # to ensure quality
        if (numPairs > 10 and score > 0.95):
            yield moviePair, (score, numPairs)

    def mapper_sort_similarities(self, moviePair, scores):
        # Shuffle things around so the key is (movie1, score)
        # so we have meaningfully sorted results.
        score, n = scores
        movie1, movie2 = moviePair

        yield (self.movieNames[int(movie1)], score), \
            (self.movieNames[int(movie2)], n)

    def reducer_output_similarities(self, movieScore, similarN):
        # Output the results.
        # Movie => Similar Movie, score, number of co-ratings
        movie1, score = movieScore
        for movie2, n in similarN:
            yield movie1, (movie2, score, n)


if __name__ == '__main__':
    MovieSimilarities.run()
